# This info is outdated #
It's kept around because it was a good general introduction to bzr and launchpad.

See SourceControl for updated info.

# Bazaar #
Testoob is being developed with Bazaar, hosted on launchpad: http://launchpad.net/testoob

# Subversion mirror #
We maintain a read-only subversion mirror on the Google Code svn server: http://testoob.googlecode.com/svn/trunk

# Getting Started #
Quick guide. Also check out [this 5-minute tutorial](http://doc.bazaar-vcs.org/bzr.dev/en/mini-tutorial/index.html).
  1. Create a user on [Launchpad](https://launchpad.net)
  1. Create a SSH keypair
    * Upload the public key to Launchpad ("change details" in your profile page, look for a  "SSH Keys" submenu)
    * Load your private key with ssh-agent on `*`nix or [Pageant](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html) on Windows.
  1. Install Bazaar (from [here](https://launchpad.net/bzr/+download) or your system's package management system)
  1. Run the following (I don't use my real email, you can decide for yourself):
```
bzr whoami "John Doe <john@example.com>"
```
  1. Create a shared repository (helps with cheap branching later):
```
bzr init-repo --rich-root testoob
```
  1. Get the trunk:
```
cd testoob
bzr branch lp:testoob trunk
```

# Working on features #
  * Create a local branch and work on it there:
```
cd testoob
bzr branch trunk myfeature
cd myfeature
# work here
```
  * Occasionally, merge the latest changes from trunk:
```
cd ../trunk
bzr pull
cd ../myfeature
bzr pull ../trunk
```
  * When you want to share, push to a private branch or personal branch on Launchpad - see links below. Notify on the mailing list so everyone knows to take a look.

# Getting the source #
To get Testoob's latest trunk:
```
bzr branch lp:testoob
```

To update your local branch:
```
bzr pull
```

# Contributing #

Bazaar makes it easy to contribute regardless of "commit access". Your name stays on the commits.
  * You can push to a [personal branch](https://help.launchpad.net/Code/PersonalBranches) on Launchpad and let us know (we can pull the changes from there)
  * You can create a [bundle](http://bazaar-vcs.org/BzrGivingBack) file and send it:
```
bzr bundle -o bundle.patch
```

If you're part of the Testoob team:
  * Push to a private branch: see the [Launchpad docs](https://help.launchpad.net/Code/UploadingABranch)
  * Push to trunk:
```
bzr push lp:testoob
```