"""Git sync service."""

import os
import re
import time
import multiprocessing
import argparse
from git import Repo, exc


class DaemonProcess(multiprocessing.Process):
    """Git sync daemon process."""

    def __init__(
        self,
        repo_url,
        repo_credentials,
        repo_path,
    ):
        super().__init__()

        self.repo_url = repo_url
        self.repo_credentials = repo_credentials
        self.repo_path = repo_path
        self.repo = None

    def run(self):
        """Run the daemon process."""

        self.setup_repo()
        while True:
            time.sleep(10)
            try:
                self.update()
            except Exception as exp:  # pylint: disable=broad-except
                print(f"Error occurred: {exp}")

    def setup_repo(self):
        """Clone the repo"""

        self.repo = self.clone_or_open_repo()
        if not self.repo:
            raise Exception(  # pylint: disable=broad-exception-raised
                "Git repository initialization failed."
            )

    def clone_or_open_repo(self):
        """Clone the repo if it doesn't exist, otherwise open it."""

        if not os.path.exists(self.repo_path):
            return Repo.clone_from(self.formatted_git_url(), self.repo_path)
        return Repo(self.repo_path)

    def formatted_git_url(self):
        """Return the git url with credentials."""

        return self.repo_url.replace("https://", f"https://{self.repo_credentials}@")

    def update(self):
        """Update the repo."""

        if self.repo_has_conflicts() or self.repo_is_dirty():
            self.commit_local_changes()

        return self.fetch_and_merge_changes()

    def repo_has_conflicts(self):
        """Check if the repo has merge conflicts."""

        return any(self.has_conflict_markers(f) for f in self.find_conflicted_files())

    def find_conflicted_files(self):
        """Find conflicted files in the repo."""

        unmerged_blobs = self.repo.index.unmerged_blobs()
        return {
            path
            for path, blobs in unmerged_blobs.items()
            if any(stage != 0 for stage, _ in blobs)
        }

    def has_conflict_markers(self, file_path):
        """Check if the file has conflict markers."""

        conflict_markers = re.compile(r"^<<<<<<< |^======= |^>>>>>>> ", re.M)
        with open(file_path, "r", encoding="utf-8") as file:
            return bool(conflict_markers.search(file.read()))

    def repo_is_dirty(self):
        """Check if the repo has uncommitted changes."""

        return self.repo.is_dirty(untracked_files=True)

    def commit_local_changes(self):
        """Commit local changes and return True if successful."""

        self.repo.git.add(A=True)
        self.repo.index.commit("Auto-commit by daemon process")

    def fetch_and_merge_changes(self):
        """Fetch and merge changes from remote and return True if successful."""

        try:
            origin = self.repo.remotes.origin
            origin.fetch()
            local_commit = self.repo.head.commit
            remote_commit = origin.refs[self.repo.active_branch.name].commit

            is_behind = sum(
                1 for x in self.repo.iter_commits(f"{local_commit}..{remote_commit}")
            )
            is_ahead = sum(
                1 for x in self.repo.iter_commits(f"{remote_commit}..{local_commit}")
            )

            if is_behind or is_ahead:
                print(f"Is behind: {is_behind}, is ahead: {is_ahead}")

            if is_behind:
                origin.pull()
                return self.resolve_conflicts_if_any()

            if is_ahead:
                origin.push()

            return False
        except exc.GitCommandError as exp:
            print(f"Git operation failed: {exp}")
            return False

    def resolve_conflicts_if_any(self):
        """Resolve conflicts if any and return True if successful."""

        if self.repo_has_conflicts():
            print("Merge conflicts detected after pull. Waiting for manual resolution.")
            return False
        return True


def main():
    """Main entry."""

    parser = argparse.ArgumentParser()

    # 添加参数
    parser.add_argument("--repo-path", required=True, help="本地克隆仓库的路径")
    parser.add_argument("--repo-url", required=True, help="仓库的远程URL")
    parser.add_argument("--repo-credentials", required=True, help="访问远程仓库的凭证")

    # 解析命令行参数
    args = parser.parse_args()

    repo_path = args.repo_path
    repo_url = args.repo_url
    repo_credentials = args.repo_credentials

    daemon = DaemonProcess(repo_url, repo_credentials, repo_path)
    daemon.start()


if __name__ == "__main__":
    main()
