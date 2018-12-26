import subprocess

from codebench.parsing.DefaultArgParser import default_arg_parser
from codebench.parsing.ConfParser import parse_config_args
from codebench.performance.Runner import Runner
from codebench.report.Factory import reporter_factory
from codebench.GitHandler import GitHandler


def reset_git_head(git_handler):
    git_handler.reset_head()


def main():
    args = default_arg_parser().parse_args()

    if not args.no_config:
        args = parse_config_args(args.config)

    # run the preparation script
    if args.before_all:
        # a blocking call to get prepared for benchmarking
        subprocess.call(args.before_all)

    start_script = args.script

    git_handler = GitHandler(args.git_folder)

    reporters = reporter_factory(args.report_types)

    # run benchmark on given commits or head
    if args.commits:
        commits = args.commits
    else:
        commits = ['head']

    if args.baseline:
        commits.append(args.baseline)

    for commit in commits:
        try:
            git_handler.checkout(commit)
            if args.before_each:
                subprocess.call(args.before_each)
            r = Runner(start_script)
            r.run()
            for reporter in reporters:
                reporter.add_result(commit, r.summary)
            if args.after_each:
                subprocess.call(args.after_each)
        except Exception as e:
            reset_git_head(git_handler)
            raise e

    for reporter in reporters:
        reporter.generate_report()
    reset_git_head(git_handler)

    if args.after_all:
        subprocess.call(args.after_all)
