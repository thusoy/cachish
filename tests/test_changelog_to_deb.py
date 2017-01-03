import sys
import textwrap

sys.path.append('tools')

from changelog_to_deb import convert_changelog as uut


def test_simple_changelog():
    changelog = textwrap.dedent('''\
        # Change log

        1.0.0 - 2016-12-23
        ==================

        First release.
    ''')
    assert uut(changelog, 'cachish', 'Tarjei Husøy', 'git@thusoy.com') == textwrap.dedent('''\
        cachish (1.0.0) unstable; urgency=low

          First release.

         -- Tarjei Husøy <git@thusoy.com>  Fri, 23 Dec 2016 12:00:00 +0000
    ''')


def test_multiline_changelog():
    changelog = textwrap.dedent('''\
        # Change log

        Some text that should be skipped.

        1.0.1 - 2016-01-05
        ==================

        ## Fixed
        - Some bug.


        1.0.0 - 2016-01-01
        ==================

        General notes.

        ## Added
        - Point one.
        - Point two.

        ## Changed
        - Point three over
          multiple lines.
    ''')
    assert uut(changelog, 'cachish', 'Tarjei Husøy', 'git@thusoy.com') == textwrap.dedent('''\
        cachish (1.0.1) unstable; urgency=low

          * Fixed: Some bug.

         -- Tarjei Husøy <git@thusoy.com>  Tue, 05 Jan 2016 12:00:00 +0000

        cachish (1.0.0) unstable; urgency=low

          General notes.
          * Added: Point one.
          * Added: Point two.
          * Changed: Point three over
            multiple lines.

         -- Tarjei Husøy <git@thusoy.com>  Fri, 01 Jan 2016 12:00:00 +0000
    ''')
