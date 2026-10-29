pySim - Tools for reading, decoding, browsing SIM/USIM/ISIM/HPSIM/eUICC Cards
=============================================================================

This repository contains a number of Python programs related to working with
subscriber identity modules of cellular networks, including but not limited
to SIM, UICC, USIM, ISIM, HPSIMs and eUICCs.

* `pySim-shell.py` can be used to interactively explore, read and decode contents
  of any of the supported card models / card applications.  Furthermore, if
  you have the credentials to your card (ADM PIN), you can also write to the card,
  i.e. edit its contents.
* `pySim-read.py` and `pySim-prog.py` are _legacy_ tools for batch programming
  some very common parameters to an entire batch of programmable cards
* `pySim-trace.py` is a tool to do an in-depth decode of SIM card protocol traces
  such as those obtained by [Osmocom SIMtrace2](https://osmocom.org/projects/simtrace2/wiki)
  or [osmo-qcdiag](https://osmocom.org/projects/osmo-qcdiag/wiki).
* `osmo-smdpp.py` is a proof-of-concept GSMA SGP.22 Consumer eSIM SM-DP+ for lab/research
* there are more related tools, particularly in the `contrib` directory.

Note that the access control configuration of normal production cards
issue by operators will restrict significantly which files a normal
user can read, and particularly write to.

The full functionality of pySim hence can only be used with on so-called
programmable SIM/USIM/ISIM/HPSIM cards, such as the various
[sysmocom programmable card products](https://shop.sysmocom.de/SIM/).

Such SIM/USIM/ISIM/HPSIM cards are special cards, which - unlike those
issued by regular commercial operators - come with the kind of keys that
allow you to write the files/fields that normally only an operator can
program.

This is useful particularly if you are running your own cellular
network, and want to configure your own SIM/USIM/ISIM/HPSIM cards for
that network.


Homepage
--------

Please visit the [official homepage](https://osmocom.org/projects/pysim/wiki)
for usage instructions, manual and examples.


Documentation
-------------

The pySim user manual can be built from this very source code by means
of sphinx (with sphinxcontrib-napoleon and sphinx-argparse).  See the
Makefile in the 'docs' directory.

A pre-rendered HTML user manual of the current pySim 'git master' is
available from <https://downloads.osmocom.org/docs/latest/pysim/> and
a downloadable PDF version is published at
<https://downloads.osmocom.org/docs/latest/osmopysim-usermanual.pdf>.

A slightly dated video presentation about pySim-shell can be found at
<https://media.ccc.de/v/osmodevcall-20210409-laforge-pysim-shell>.


pySim-shell vs. legacy tools
----------------------------

While you will find a lot of online resources still describing the use of
`pySim-prog.py` and `pySim-read.py`, those tools are considered legacy by
now and have by far been superseded by the much more capable
`pySim-shell.py`.  We strongly encourage users to adopt pySim-shell, unless
they have very specific requirements like batch programming of large
quantities of cards, which is about the only remaining use case for the
legacy tools.


Changing an IMSI prefix
----------------------

Use `pySim-imsi-prefix.sh` to read the current IMSI, authenticate with ADM1,
replace its leading digits and verify the result. For PC/SC reader 0:

```sh
./pySim-imsi-prefix.sh -p 0 26201 --dry-run
./pySim-imsi-prefix.sh -p 0 26201
```

Both commands wait for a SIM and then continue automatically as cards are
removed and replaced. Stop with Ctrl+C, or use `--once` to process one SIM.
The script waits for removal before accepting the next insertion, so it does
not repeatedly process a SIM left in the reader. A failed SIM is not retried.

The second command prompts for ADM1 without echoing it for each SIM. Alternatively,
supply a shared PIN with `--adm1 VALUE`. ADM1 accepts up to eight printable ASCII characters or 16 hex
digits. Authentication is attempted once. The Bash script uses `pySim-shell.py`
with the repository's `venv/bin/python`, falling back to `python3`.
Set `PYSIM_PYTHON` to select a different Python executable.

For example, prefix `26201` changes `999700000192019` to `262010000192019`.
The script replaces exactly as many leading digits as supplied (five or six),
preserving the IMSI length. It defaults to `ADF.USIM/EF.IMSI`; use
`--application sim` for `DF.GSM/EF.IMSI`. Only the selected EF.IMSI is written;
EF.AD (including MNC length), PLMN lists and ISIM identities are unchanged.


Enabling and disabling ISIM on sysmocom SJA5
------------------------------------------

`disable-isim.sh` selects USIM IMS fallback by locking the ISIM application,
removing only its record(s) from EF.DIR, clearing the associated USIM IMS/ePDG
service bits, and deactivating the corresponding USIM IMS files. It preserves
ordinary SIM/USIM identities, authentication keys, SMS storage and 5GS settings.
This follows the mechanism described in section 9.1 of the
[sysmoISIM-SJA5 manual](https://sysmocom.de/manuals/sysmoisim-sja5-manual.pdf).
It does not by itself prove that a particular phone or network supports VoLTE/VoWiFi.

The bare commands detect the inserted card and manage backups outside the repository:

```sh
./disable-isim.sh --dry-run
./disable-isim.sh
./enable-isim.sh
```

The first disable creates a backup under
`~/.local/state/pysim/isim/ICCID/before-disable-TIMESTAMP.json`; both commands then
reuse the most recent backup for that same ICCID. This lets an interrupted disable
resume, and keeps the original enabled state across repeated toggles.
`XDG_STATE_HOME` overrides `~/.local/state`.
Both commands display the detected ICCID and backup path. Backups are retained
across enable/disable cycles. Enabling without a matching backup stops before
authentication. To require an expected ICCID or use a specific backup instead:

```sh
iccid=YOUR_CARD_ICCID
backup="$HOME/.cache/pysim/isim-$iccid-before-disable.json"
mkdir -p -- "$(dirname -- "$backup")"

# Read-only preview: no PIN verification, secure-channel authentication or writes.
./disable-isim.sh --iccid "$iccid" --backup "$backup" --dry-run

# Back up the original state, then disable ISIM. Prompts for ADM1 without echo.
./disable-isim.sh --iccid "$iccid" --backup "$backup"

# Restore the original state, including originally disabled files and service bits.
./enable-isim.sh --iccid "$iccid" --backup "$backup" --dry-run
./enable-isim.sh --iccid "$iccid" --backup "$backup"
```

Both wrappers accept `-p READER` (default 0) and use `venv/bin/python`; override
the executable with `PYSIM_PYTHON`. For unattended use, ADM1 can be supplied via
`PYSIM_ADM1`. Do not put credentials in scripts or version control. The helper reads
the SJA5 issuer SCP02 keyset (security domain 0, key version 0x70) from the
ADM1-protected card file; it does not guess keys or retry failed authentication.
Cards whose issuer keys cannot be read in this way are not supported.

New backups are created with mode 0600 and never overwrite an existing file. A
matching existing backup is validated and reused, including after partial failure.
Use a new explicit `--backup` path to start from a deliberately changed baseline.
The backup contains
subscriber identifiers and the original directory/service/lifecycle state, but no
PINs or authentication/management keys. Keep it: enabling requires the original
backup, checks the ICCID, and refuses to overwrite unrelated directory or service
changes made since disabling. If an operation stops after writes began, reconnect
the same card and run the enable command with that backup. Each operation stops on
the first failure; successful writes are read back. The tool resets the card when
switching from GlobalPlatform management back to ordinary UICC file access, then
verifies the same supplied ADM1 in the fresh session. Failed verification is never
retried. No applet is deleted.

Power-cycle the phone or remove/reinsert the SIM after changing the card. Enabling
restores the original ISIM contents; it does not populate missing IMPI, IMPU, domain
or P-CSCF values. The initial inspection in `osmocom-sim-report.md` remains an
unchanged historical snapshot.


Git Repository
--------------

You can clone from the official Osmocom  git repository using
```
git clone https://gitea.osmocom.org/sim-card/pysim.git
```

There is a web interface at <https://gitea.osmocom.org/sim-card/pysim>.


Installation
------------

Please install the following dependencies:

 - bidict
 - cmd2 >= 1.5.0
 - colorlog
 - construct >= 2.9.51
 - pyosmocom
 - jsonpath-ng
 - packaging
 - pycryptodomex
 - pyscard
 - pyserial
 - pytlv
 - pyyaml >= 5.4
 - smpp.pdu (from `github.com/hologram-io/smpp.pdu`)
 - termcolor

Example for Debian:
```sh
sudo apt-get install --no-install-recommends \
	pcscd libpcsclite-dev \
	python3 \
	python3-setuptools \
	python3-pycryptodome \
	python3-pyscard \
	python3-pip
pip3 install --user -r requirements.txt
```

After installing all dependencies, the pySim applications ``pySim-read.py``, ``pySim-prog.py`` and ``pySim-shell.py`` may be started directly from the cloned repository.

In addition to the dependencies above ``pySim-trace.py`` requires ``tshark`` and the python package ``pyshark`` to be installed. It is known that the ``tshark`` package
in Debian versions before 11 may not work with pyshark.

### Archlinux Package

Archlinux users may install the package ``python-pysim-git``
[![](https://img.shields.io/aur/version/python-pysim-git)](https://aur.archlinux.org/packages/python-pysim-git)
from the [Arch User Repository (AUR)](https://aur.archlinux.org).
The most convenient way is the use of an [AUR Helper](https://wiki.archlinux.org/index.php/AUR_helpers),
e.g. [yay](https://aur.archlinux.org/packages/yay) or [pacaur](https://aur.archlinux.org/packages/pacaur).
The following example shows the installation with ``yay``.

```sh
# Install
yay -Sy python-pysim-git

# Uninstall
sudo pacman -Rs python-pysim-git
```


Forum
-----

We welcome any pySim related discussions in the
[SIM Card Technology](https://discourse.osmocom.org/c/sim-card-technology/)
section of the osmocom discourse (web based Forum).


Mailing List
------------

There is no separate mailing list for this project. However,
discussions related to pySim are happening on the simtrace
<simtrace@lists.osmocom.org> mailing list, please see
<https://lists.osmocom.org/mailman/listinfo/simtrace> for subscription
options and the list archive.

Please observe the [Osmocom Mailing List
Rules](https://osmocom.org/projects/cellular-infrastructure/wiki/Mailing_List_Rules)
when posting.

Issue Tracker
-------------

We use the [issue tracker of the pysim project on osmocom.org](https://osmocom.org/projects/pysim/issues) for
tracking the state of bug reports and feature requests.  Feel free to submit any issues you may find, or help
us out by resolving existing issues.


Contributing
------------

Our coding standards are described at
<https://osmocom.org/projects/cellular-infrastructure/wiki/Coding_standards>

We are using a gerrit-based patch review process explained at
<https://osmocom.org/projects/cellular-infrastructure/wiki/Gerrit>
