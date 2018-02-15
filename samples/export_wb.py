#
# This sample uses the PyPDF2 library for combining pdfs together to get the full pdf for all the views in a
# workbook.
#
# You will need to do `pip install PyPDF2` to use this sample.
#

import argparse
import getpass
import logging
import tempfile
import shutil
import functools
import os.path

import tableauserverclient as TSC
try:
    import PyPDF2
except ImportError:
    print('Please `pip install PyPDF2` to use this sample')
    import sys
    sys.exit(1)


def get_views_for_workbook(server, workbook_id):  # -> Iterable of views
    workbook = server.workbooks.get_by_id(workbook_id)
    server.workbooks.populate_views(workbook)
    return workbook.views


def download_pdf(server, views, tempdir, view_id):  # -> Filename to downloaded pdf
    logging.info("Exporting {}".format(view_id))
    view = next((x for x in views if x.id == view_id))
    destination_filename = os.path.join(tempdir, view_id)
    server.views.populate_pdf(view)
    with file(destination_filename, 'wb') as f:
        f.write(view.pdf)

    return destination_filename


def combine_into(dest_pdf, filename):  # -> None
    dest_pdf.append(filename)
    return dest_pdf


def cleanup(tempdir):
    shutil.rmtree(tempdir)


def main():
    parser = argparse.ArgumentParser(description='Export to PDF all of the views in a workbook')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--site', '-S', default=None)
    parser.add_argument('-p', default=None)

    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    parser.add_argument('--file', '-f', help='filename to store the exported data')
    parser.add_argument('resource_id', help='LUID for the view')

    args = parser.parse_args()

    if args.p is None:
        password = getpass.getpass("Password: ")
    else:
        password = args.p

    if args.file:
        filename = args.file
    else:
        filename = 'out.pdf'

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tempdir = tempfile.mkdtemp('tsc')
    logging.debug("Saving to tempdir: %s", tempdir)

    tableau_auth = TSC.TableauAuth(args.username, password, args.site)
    server = TSC.Server(args.server, use_server_version=True)
    try:
        with server.auth.sign_in(tableau_auth):
            views = list(TSC.Pager(server.views))
            get_list = functools.partial(get_views_for_workbook, server)
            download = functools.partial(download_pdf, server, views, tempdir)

            view_list = (x.id for x in get_list(args.resource_id))
            downloaded = (download(x) for x in view_list)
            output = reduce(combine_into, downloaded, PyPDF2.PdfFileMerger())
            with file(filename, 'wb') as f:
                output.write(f)
    finally:
        cleanup(tempdir)


if __name__ == '__main__':
    main()
