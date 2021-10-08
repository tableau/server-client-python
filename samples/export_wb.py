####
# This sample uses the PyPDF2 library for combining pdfs together to get the full pdf for all the views in a
# workbook.
#
# You will need to do `pip install PyPDF2` to use this sample.
#
# To run the script, you must have installed Python 3.6 or later.
####


import argparse
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


def download_pdf(server, tempdir, view):  # -> Filename to downloaded pdf
    logging.info("Exporting {}".format(view.id))
    destination_filename = os.path.join(tempdir, view.id)
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
    parser = argparse.ArgumentParser(description='Export to PDF all of the views in a workbook.')
    # Common options; please keep those in sync across all samples
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--site', '-S', help='site name')
    parser.add_argument('--token-name', '-p', required=True,
                        help='name of the personal access token used to sign into the server')
    parser.add_argument('--token-value', '-v', required=True,
                        help='value of the personal access token used to sign into the server')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    # Options specific to this sample
    parser.add_argument('--file', '-f', default='out.pdf', help='filename to store the exported data')
    parser.add_argument('resource_id', help='LUID for the workbook')

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tempdir = tempfile.mkdtemp('tsc')
    logging.debug("Saving to tempdir: %s", tempdir)

    try:
        tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
        server = TSC.Server(args.server, use_server_version=True)
        with server.auth.sign_in(tableau_auth):
            get_list = functools.partial(get_views_for_workbook, server)
            download = functools.partial(download_pdf, server, tempdir)

            downloaded = (download(x) for x in get_list(args.resource_id))
            output = reduce(combine_into, downloaded, PyPDF2.PdfFileMerger())
            with file(args.file, 'wb') as f:
                output.write(f)
    finally:
        cleanup(tempdir)


if __name__ == '__main__':
    main()
