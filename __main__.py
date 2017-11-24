# pylint: disable=invalid-name
# pylint: disable=misplaced-comparison-constant
# pylint: disable=wrong-import-position
"""
This file provides a procedural script to generate shortcodes for all available
versions of pylint
"""

import os
import re
import shutil
import subprocess
import time

import htmlmin
from jinja2 import Environment, FileSystemLoader
import virtualenv

ROOT_DIR = os.path.join(
    os.getcwd(),
    os.path.dirname(__file__)
)
VIRTUALENV_DIR = os.path.join(ROOT_DIR, '.venv')

virtualenv.create_environment(VIRTUALENV_DIR)
if 'nt' == os.name:
    activate_path = os.path.join(VIRTUALENV_DIR, "Scripts", "activate_this.py")
else:
    activate_path = os.path.join(VIRTUALENV_DIR, "bin", "activate_this.py")
execfile(activate_path, dict(__file__=activate_path))

PIP_PATH = os.path.join(VIRTUALENV_DIR, 'bin', 'pip')
PYLINT_PATH = os.path.join(VIRTUALENV_DIR, 'bin', 'pylint')

VERSION_NUMBER_LIST = os.path.join(ROOT_DIR, 'version_numbers')
WORKING_FILES_DIR = os.path.join(ROOT_DIR, 'raw')
if os.path.isdir(WORKING_FILES_DIR):
    shutil.rmtree(WORKING_FILES_DIR)
os.makedirs(WORKING_FILES_DIR)
VERSION_FILES_DIR = os.path.join(ROOT_DIR, 'dist', 'versions')
if os.path.isdir(VERSION_FILES_DIR):
    shutil.rmtree(VERSION_FILES_DIR)
os.makedirs(VERSION_FILES_DIR)
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')
JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR)
)
SHORTCODE_PATTERN = re.compile(r'''
\s*                 # include potential initial space
\:                  # begins with a colon
(?P<wordy>          # descriptive-name-of-code
    [\w\-]+         # is word characters and dash
)
\s+                 # spacing
\(                  # open bracket
(?P<number>         # code number
    \w+             # letter and some digits
)
\)                  # close bracket
:                   # descriptor ends
\s+                 # spacing
\*                  # parsed message wrapped in asterisks
(?P<message>        # parsed message
    [^*]+           # everything until the next asterisk
)
\*                  # close parsed message
\s+                 # spacing including newlines
(?P<details>        # pull the full detail
    (               # capture single character
        [\s\S]      # can be anything
        (?<!\n\:)   # so long as newline colon is not following
    )+              # repeat greedily
)
\s+                 # include final space
''', re.VERBOSE)
MAX_VERSION_LIST_AGE = 60 * 60 * 24 * 7
MAX_SHORTCODE_FILE_AGE = 60 * 60 * 24 * 7 * 30


def get_cached_version_numbers():
    """Loads the version_numbers cache file"""
    with open(VERSION_NUMBER_LIST, 'r+') as cache_file:
        version_numbers = cache_file.read().strip().split('\n')
    return version_numbers


def check_list_cache_age():
    """Checks the age of the included version list"""
    try:
        assert (
            os.path.getmtime(VERSION_NUMBER_LIST)
            >=
            (int(time.time()) - MAX_VERSION_LIST_AGE)
        )
    except (AssertionError, OSError):
        return get_fresh_version_numbers()
    else:
        return get_cached_version_numbers()


def get_fresh_version_numbers():
    """Gets a full list of pylint versions"""
    print 'Installing base pylint to get version list'
    version_results = subprocess.check_output(
        [
            PIP_PATH,
            'install',
            '--upgrade',
            '-v',
            'pylint'
        ]
    )
    print 'Finished installing; parsing log'
    version_numbers = list()
    for version_line_match in re.finditer(
            r'^\s*Using.+?versions:(?P<version_list>.+)\)$',
            version_results, re.MULTILINE
    ):
        for version_number_match in re.finditer(
                r'(?P<full_semver>(\d+\.?)+)',
                version_line_match.group('version_list')
        ):
            version_numbers.append(
                version_number_match.group('full_semver')
            )
    version_numbers = sorted(set(version_numbers))[::-1]
    with open(VERSION_NUMBER_LIST, 'w+') as cache_file:
        for version_number in version_numbers:
            cache_file.write(version_number + '\n')
    print "Finished parsing; discovered these versions: %s" % (', '.join(version_numbers))
    # remove_pylint()
    return version_numbers


def install_specific_pylint_version(version_number):
    """Installs a specific version of pylint"""
    print "Installing pylint==%s" % (version_number)
    # print ' '.join([
    #     PIP_PATH,
    #     'install',
    #     '--quiet',
    #     "pylint==%s" % (version_number)
    # ])
    print subprocess.check_output(
        [
            PIP_PATH,
            'install',
            '--quiet',
            "pylint==%s" % (version_number)
        ]
    )
    print "Finished installing %s" % (version_number)


def convert_version_number_to_raw_filename(version_number):
    """Simplifies finding a version number's raw output"""
    return os.path.join(
        WORKING_FILES_DIR,
        ("raw_%s.txt" % (version_number.replace('.', '_')))
    )


def get_version_shortcodes(version_number):
    """Attempts to run the --list-msgs command"""
    print "Attempting to find shortcodes for %s" % (version_number)
    try:
        shortcodes = subprocess.check_output([PYLINT_PATH, '--list-msgs'])
    except subprocess.CalledProcessError:
        print(
            'ERROR: pylint --list-msgs raised an error; '
            'writing nothing to its output'
        )
        shortcodes = 'NOPE'
    with open(
        convert_version_number_to_raw_filename(version_number),
        'w+'
    ) as raw_output:
        raw_output.write(shortcodes)
    return shortcodes


def parse_raw_shortcodes(version_number, raw_shortcodes):  # pylint: disable=unused-argument
    """Parses the full list of shortcodes"""
    list_of_shortcodes = list()
    for shortcode_match in re.finditer(SHORTCODE_PATTERN, raw_shortcodes):
        shortcode = type('', (), {})()
        for key in ['wordy', 'number', 'message', 'details']:
            setattr(
                shortcode,
                key,
                re.sub(r'\s+', ' ', shortcode_match.group(key))
            )
        list_of_shortcodes.append(shortcode)
    return list_of_shortcodes


def parse_shortcodes_from_working_files(version_number):
    """Loads the shortcodes from the working directory"""
    with open(
        convert_version_number_to_raw_filename(version_number),
        'r+'
    ) as raw_file:
        raw_shortcodes = raw_file.read()
    return parse_raw_shortcodes(version_number, raw_shortcodes)


def convert_version_number_to_out_filename(version_number):
    """Converts the version number to its out filename"""
    return (
        os.path.join(
            VERSION_FILES_DIR,
            "%s.html" % (version_number.replace('.', '_'))
        )
    )


def compile_version_template(version_number, shortcodes):
    """Compiles the finishes template per version number"""
    template = JINJA_ENV.get_template('version.html.j2')
    rendered_template = template.render(
        version_number=version_number,
        shortcodes=shortcodes
    )
    minified = htmlmin.minify(rendered_template)
    with open(
        convert_version_number_to_out_filename(version_number),
        'w+'
    ) as final_page:
        final_page.write(minified)


def parse_a_version(version_number):
    """Runs all the necessary methods for a specific version number"""
    print "Parsing version %s" % (version_number)
    install_specific_pylint_version(version_number)
    raw_shortcodes = get_version_shortcodes(version_number)
    # cleaned_shortcodes = parse_shortcodes_from_working_files(version_number)
    cleaned_shortcodes = parse_raw_shortcodes(version_number, raw_shortcodes)
    compile_version_template(version_number, cleaned_shortcodes)


def compile_index_template(version_numbers):
    """Compiles the index"""
    template = JINJA_ENV.get_template('index.html.j2')
    rendered_template = template.render(
        version_numbers=version_numbers
    )
    with open(
        os.path.join(VERSION_FILES_DIR, '..', 'index.html'),
        'w+'
    ) as final_page:
        final_page.write(rendered_template)


def commit_and_push():
    """Commits changes and pushes the repo"""
    subprocess.check_output(['git', 'add', '--all'])
    subprocess.check_output(['git', 'commit', '-m', 'script update'])
    subprocess.check_output(['git', 'push'])
    subprocess.check_output(
        ['git', 'subtree', 'split', '--prefix', 'dist', '-b', 'gh-pages'])
    subprocess.check_output(
        ['git', 'push', '-f', 'origin', 'gh-pages:gh-pages'])
    subprocess.check_output(['git', 'branch', '-D', 'gh-pages'])


def cli_runner():
    """Runs the functions in the proper order"""
    version_numbers = get_fresh_version_numbers()
    for version_number in version_numbers:
        parse_a_version(version_number)
    compile_index_template(version_numbers)
    commit_and_push()


cli_runner()
