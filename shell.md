# local run
python gitlab_commit_stats.py -t JZiz8Z5ewz6gu_SWSSay -s "2021-11-01 00:00:00" -u "2021-11-05 23:59:59" -a https://gitlab2.bitautotech.com/api/v4

# docker build
```shell

docker build -t python-git-stats:v1.0 .

docker run --rm -it python-git-stats:v1.0

```