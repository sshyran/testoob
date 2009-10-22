import sys
import optparse
import getpass

import gdata.projecthosting.client
import gdata.projecthosting.data
import gdata.gauth
import gdata.client
import gdata.data
import atom.http_core
import atom.core

CLIENT_NAME = "testoob_googlecode_issues"

def die(msg):
    print >>sys.stderr, msg
    sys.exit(1)

def get_optparser():
    p = optparse.OptionParser()
    p.add_option("--user", "-u", metavar="USERNAME")
    p.add_option("--project", "-p")
    return p

def get_issues_client(username):
    password = getpass.getpass("Password for user '%s': " % username)

    issues_client = gdata.projecthosting.client.ProjectHostingClient()

    try:
        issues_client.client_login(username, password, CLIENT_NAME)
    except gdata.client.BadAuthentication, e:
        die("Couldn't authenticate user '%s': %s" % (username, e))

    return issues_client

def main(args):
    optparser = get_optparser()

    opts, args = optparser.parse_args()

    if opts.project is None:
        optparser.error("Missing required option 'project'")
    if opts.user is None:
        optparser.error("Missing required option 'user'")


    client = get_issues_client(opts.user)
    issues_feed = client.get_issues(opts.project)
    for issue in issues_feed.entry:
        print issue.title.text

if __name__ == "__main__":
    main(sys.argv)
