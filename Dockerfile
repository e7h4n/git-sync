FROM python:3

COPY gitsync/ ./git-sync/gitsync
COPY setup.py ./git-sync/
COPY README.md ./git-sync/
RUN cd git-sync && pip install --no-cache-dir -e .

ENTRYPOINT ["git-sync"]
CMD ["--repo-path", "/tmp/beancount", "--repo-url", "", "--repo-credentials", ""]
