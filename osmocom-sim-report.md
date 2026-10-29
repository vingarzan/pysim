# SIM card inspection report

Inspection date: **2026-10-29** (Europe/Berlin; client date).

Read directly from the card in the local PC/SC reader using this checkout of pySIM. “ISM” is interpreted as **ISIM**, the IMS subscriber application. Subscriber identities below are sensitive; PINs, PUKs, long-term authentication keys, OP/OPc, and cached security-key material are omitted.

## Findings

- Card model detected by pySIM: **SysmocomSJA5**; UICC with legacy GSM SIM, USIM, and ISIM filesystem support.
- ICCID **8949440000001920006**. The legacy SIM and USIM both contain IMSI **262010000192000**. Both administrative-data files specify a **two-digit MNC**, giving home PLMN **262-01**.
- **ISIM identities are unprovisioned:** IMPI, home domain, and all eight IMPU records contain an empty `80 00` TLV followed by `ff` padding. All eight P-CSCF address records are `ff`. The presence of ISIM and advertised IMS services does not establish a usable IMS subscription.
- All five inspected SIM/USIM/ISIM authentication-key files select **Milenage**, use **OPc**, and contain matching 128-bit key and OPc values. Values are omitted. This comparison does not test authentication against a network.
- No MSISDN is stored in the inspected SIM/USIM number records. The main SIM phonebook is empty, and both inspected SMS stores report all 30 slots free.
- SIM and USIM SMS parameters contain service-centre digits **3548900076**, TON **unknown**, numbering plan **ISDN/E.164**. No leading `+` is inferred from that TON.
- 5GS files exist and services 122, 123, and 126 are set, but subscription-identifier privacy (124) and USIM SUCI calculation (125) are unset. SUCI calculation files contain an empty `a0 00` list plus padding and fail this pySIM decoder. No home-network public key was identified in those bytes.
- ADM1 verification succeeded once. No PIN1/PIN2 or other administrative credential was attempted. Seven files remain blocked by security status; 18 return invalidated-data status; 17 model-known files were not found.

## Card and acquisition

| Property | Observed value |
| --- | --- |
| Reader | Cherry GmbH SmartTerminal XX44 00 00 (PC/SC index 0) |
| ATR | 3b9f96801f878031e073fe211b674a357530350265f8 |
| ICCID | 8949440000001920006 |
| pySIM revision | 51da6263b77dd8c1325b44dbc31e4ac46c9fd1da |
| Python | Existing venv, Python 3.10; pyscard 2.3.1 |
| Card lifecycle | MF, USIM and ISIM selected as operational_activated |
| Available memory reported in FCP | 353648 bytes |
| Additional detected filesystem add-ons | GSM-R (DF.EIRENE), RUIM (DF.CDMA) |
| Other selectable application probes | GlobalPlatform ISD a000000003000000; ARA-M a00000015141434c00 |

EF.DIR advertises the full AIDs below. pySIM internally uses their application prefixes.

| Application | Full AID from EF.DIR |
| --- | --- |
| USIM | a0000000871002ffffffff8907090000 |
| ISIM | a0000000871004ffffffff8907090000 |

### Method and limits

Used `pySim-shell.py -p 0 --noprompt` and `fsdump` from MF before and after one `verify_adm` with the user-supplied credential. Raw bytes were decoded offline with this checkout’s pySIM file classes. No UPDATE, WRITE, CREATE, DELETE, ACTIVATE, DEACTIVATE, PIN change/unblock/enable/disable, or network AUTHENTICATE operation was requested. ADM verification changes session security state and may affect credential attempt bookkeeping; this was a read-only inspection of configuration, not a write operation.

The first dump stopped after 35 entries because the Python 3.10 exception class lacks Python 3.11’s `add_note`. A temporary wrapper added that exception-note method in memory. Both subsequent filesystem walks completed without the “Stopping early” marker. No repository source was changed for the workaround.

The walk covers files and directories known to the selected pySIM card model; it is not an exhaustive search of arbitrary file IDs or applets. pySIM can silently skip an unselectable directory, so missing entries are not proof that every possible file is absent. GlobalPlatform applet inventory, ARA-M rules, eUICC management, network registration, calls, and interoperability were not tested. “Empty” describes the observed allocation/padding; it does not prove the card has never been used.

All **267** files whose contents were readable in both completed dumps were byte-for-byte unchanged. Protected files first readable after ADM have no pre-ADM content baseline.

## Coverage

| Scope | Entries incl. directories/errors | Contents read | 6982 | 6984 | 6a82 |
| --- | --- | --- | --- | --- | --- |
| Legacy GSM SIM | 54 | 52 | 0 | 0 | 1 |
| Shared telecom | 29 | 23 | 0 | 0 | 2 |
| USIM | 188 | 150 | 3 | 18 | 7 |
| ISIM | 26 | 21 | 0 | 0 | 4 |
| Card OS | 14 | 6 | 4 | 0 | 3 |
| GSM-R | 24 | 23 | 0 | 0 | 0 |
| CDMA/RUIM | 5 | 4 | 0 | 0 | 0 |

Total: **347** recorded entries: **284** readable EF bodies, **20** selected directories plus **1** ISD application entry without EF contents, **7** security-status failures, **18** invalidated-data responses, **17** file-not-found responses. Directory entries are not counted as readable EF contents.

## Legacy SIM and shared telecom

| Item | Observed configuration |
| --- | --- |
| GSM IMSI | 262010000192000 |
| GSM EF.AD | 00000002; normal operation; MNC length 2 |
| USIM EF.AD | 01000802ff; pySIM: normal_and_specific_facilities; MNC length 2 |
| Access classes | EF.ACC = 0001 in SIM and USIM; class 0 set |
| Higher-priority PLMN search | EF.HPPLMN = 05 (30-minute interval) |
| Service provider name | No name stored: 00 followed by ff padding |
| PLMN preference lists | No configured PLMNs in inspected PLMNsel / PLMNwAcT / OPLMNwAcT / HPLMNwAcT |
| Forbidden PLMN list | All ff; no entries |
| GSM location | TMSI all ff; location-update status 01; no usable registered location |
| GPRS/PS location | Temporary identities unset; update status 01 |
| Phonebook | DF.TELECOM/EF.ADN: 250 records, all ff |
| MSISDN | 6 records in each inspected EF.MSISDN, all ff |
| USIM fixed dialling | 20 EF.FDN records, all ff; FDN disabled in EF.EST |
| SMS | 30 free_space records in each of DF.TELECOM/EF.SMS and ADF.USIM/EF.SMS; may be shared storage |
| SMS parameters | 2 records; first contains SMSC 3548900076, PID 00, DCS 00, validity 5 minutes; second unconfigured |
| Enabled services | USIM EF.EST = 000000000000000000; FDN, BDN and APN control disabled |
| APN control list | EF.ACL is ff padding; no usable APN entry identified |
| STK menu label | EF.SUME contains “STK Services” |

## USIM: EPS, 5GS and non-3GPP configuration

| Item | Observed configuration |
| --- | --- |
| EPS registration | EF.EPSLOCI: GUTI all ff; last TAI ffffff0000; not_updated |
| 5GS registration, 3GPP and non-3GPP | Both location files: 5G-GUTI and last TAI all ff; not_updated |
| 5GS security contexts | 3GPP/non-3GPP stored contexts and authentication-key area all ff |
| Routing indicator | 0 (raw f0ffffff) |
| SUCI calculation information | DF.5GS and DF.SAIP: a000 then ff padding; decoder error, no populated protection list/key identified |
| SUPI NAI | All ff; pySIM decode failed on empty contents |
| URSP and trusted non-3GPP serving-network name | All ff |
| UAC access identities | 03ffffff; pySIM decodes multimedia-priority and mission-critical service bits set |
| ePDG configuration | ePDG identity and selection files, including emergency variants, are ff padding; UST 106/107/110/111 unset |
| NAS configuration | EF.NASCONFIG all ff; UST 96 unset |
| Enhanced AKA | EF.eAKA: enhanced_sqn_calculation_supported = false |

### USIM service table

EF.UST raw: `beff9f9de73e04080000ff730000002600000000`. The following are **set bits**, described using this checkout’s decoder. Every unlisted bit in this 20-byte table is clear. These advertise USIM services; they do not establish network support or populated service data.

| Service | Description |
| --- | --- |
| 2 | Fixed Dialling Numbers (FDN) |
| 3 | Extension 2 |
| 4 | Service Dialling Numbers (SDN) |
| 5 | Extension3 |
| 6 | Barred Dialling Numbers (BDN) |
| 8 | Outgoing Call Information (OCI and OCT) |
| 9 | Incoming Call Information (ICI and ICT) |
| 10 | Short Message Storage (SMS) |
| 11 | Short Message Status Reports (SMSR) |
| 12 | Short Message Service Parameters (SMSP) |
| 13 | Advice of Charge (AoC) |
| 14 | Capability Configuration Parameters 2 (CCP2) |
| 15 | Cell Broadcast Message Identifier |
| 16 | Cell Broadcast Message Identifier Ranges |
| 17 | Group Identifier Level 1 |
| 18 | Group Identifier Level 2 |
| 19 | Service Provider Name |
| 20 | User controlled PLMN selector with Access Technology |
| 21 | MSISDN |
| 24 | Enhanced Multi-Level Precedence and Pre-emption Service |
| 25 | Automatic Answer for eMLPP |
| 27 | GSM Access |
| 28 | Data download via SMS-PP |
| 29 | Data download via SMS-CB |
| 32 | RUN AT COMMAND command |
| 33 | shall be set to 1 |
| 34 | Enabled Services Table |
| 35 | APN Control List (ACL) |
| 38 | GSM security context |
| 39 | CPBCCH Information |
| 40 | Investigation Scan |
| 42 | Operator controlled PLMN selector with Access Technology |
| 43 | HPLMN selector with Access Technology |
| 44 | Extension 5 |
| 45 | PLMN Network Name |
| 46 | Operator PLMN List |
| 51 | Service Provider Display Information |
| 60 | User Controlled PLMN selector for I-WLAN access |
| 81 | Home I-WLAN Specific Identifier List |
| 82 | I-WLAN Equivalent HPLMN Presentation Indication |
| 83 | I-WLAN HPLMN Priority Indication |
| 84 | I-WLAN Last Registered PLMN |
| 85 | EPS Mobility Management Information |
| 86 | Allowed CSG Lists and corresponding indications |
| 87 | Call control on EPS PDN connection by USIM |
| 88 | HPLMN Direct Access |
| 89 | eCall Data |
| 90 | Operator CSG Lists and corresponding indications |
| 93 | Communication Control for IMS by USIM |
| 94 | Extended Terminal Applications |
| 95 | Support of UICC access to IMS |
| 122 | 5GS Mobility Management Information |
| 123 | 5G Security Parameters |
| 126 | UAC Access Identities support |

## ISIM / IMS

| File | Observed contents |
| --- | --- |
| EF.IMPI | 128 bytes; 8000 + ff padding; empty private identity |
| EF.DOMAIN | 50 bytes; 8000 + ff padding; empty IMS home domain |
| EF.IMPU | 8 × 128 bytes; each 8000 + ff padding; no public identities |
| EF.P-CSCF | 8 × 128 bytes; all ff; no P-CSCF addresses |
| EF.AD | ffffff; no meaningful provisioned administrative value inferred |
| EF.IST | 190208; service bit details below |
| EF.UICCIARI | 8 records, all ff |
| EF.WebRTCURI | 10 records, all ff despite WebRTC service bit set |
| EF.IMSConfigData / XCAPConfigData / MuDMiDConfigData | BER-TLV retrieval returned no data objects ({}) |
| EF.FromPreferred | 00; associated service bit unset |
| EF.IMSDCI | ff; associated service bit unset |
| SMS files | EF.SMS, EF.SMSS, EF.SMSR and EF.SMSP returned 6a82 |
| Authentication configuration | Milenage / OPc; keys match the SIM and USIM files; values omitted |

| IST bit | Description | Set |
| --- | --- | --- |
| 1 | P-CSCF address | yes |
| 2 | Generic Bootstrapping Architecture (GBA) | no |
| 3 | HTTP Digest | no |
| 4 | GBA-based Local Key Establishment Mechanism | yes |
| 5 | Support of P-CSCF discovery for IMS Local Break Out | yes |
| 6 | Short Message Storage (SMS) | no |
| 7 | Short Message Status Reports (SMSR) | no |
| 8 | Support for SM-over-IP including data download via SMS-PP as defined in TS 31.111 [31] | no |
| 9 | Communication Control for IMS by ISIM | no |
| 10 | Support of UICC access to IMS | yes |
| 11 | URI support by UICC | no |
| 12 | Media Type support | no |
| 13 | IMS call disconnection cause | no |
| 14 | URI support for MO SHORT MESSAGE CONTROL | no |
| 15 | MCPTT | no |
| 16 | URI support for SMS-PP DOWNLOAD as defined in 3GPP TS 31.111 [31] | no |
| 17 | From Preferred | no |
| 18 | IMS configuration data | no |
| 19 | XCAP Configuration Data | no |
| 20 | WebRTC URI | yes |
| 21 | MuD and MiD configuration data | no |
| 22 | IMS Data Channel indication | no |

## Authentication and card security

ADM1 was accepted. PIN1/PIN2 verification was unnecessary for the subscriber files read here. The protected CHV1/CHV2/ADM1/ADM2 backing files still returned 6982 after ADM1; their PIN values, retry counters and enable/disable state were not obtained. No guesses or other credentials were tried.

| File | Algorithm | OP mode | Key/OPc match SIM |
| --- | --- | --- | --- |
| MF/DF.SYSTEM/EF.SIM_AUTH_KEY | milenage | OPc | yes |
| MF/ADF.USIM/EF.USIM_AUTH_KEY | milenage | OPc | yes |
| MF/ADF.USIM/EF.USIM_AUTH_KEY_2G | milenage | OPc | yes |
| MF/ADF.ISIM/EF.ISIM_AUTH_KEY | milenage | OPc | yes |
| MF/ADF.ISIM/EF.ISIM_AUTH_KEY_2G | milenage | OPc | yes |

The USIM and ISIM SQN configurations are identical: SQN check enabled, delta-max check enabled, age-limit check disabled, `skip_next_sqn_check=true`, IND length 5, delta-max and age limit 8589934592, all 32 stored freshness values zero. Those settings are observed configuration, not an authentication test.

## Additional filesystem observations

DF.EIRENE and DF.CDMA were selectable and their known files were included in the walk. DF.CDMA/EF.SPN contains the text `smartfren`; this is an additional on-card label and does not establish the current network/operator. GSM-R EF.IC contains three populated decision entries. Raw values for non-secret files appear below.

## Unreadable or unavailable files

`6982` = security status not satisfied; `6984` = referenced data invalidated; `6a82` = file not found. Invalidated data was not activated to make it readable. A failed read is not reported as empty.

| Path | Status | Meaning |
| --- | --- | --- |
| MF/DF.GSM/EF.CPBCCH | 6a82 | Wrong parameters - File not found |
| MF/DF.TELECOM/EF.CCP | 6a82 | Wrong parameters - File not found |
| MF/DF.TELECOM/EF.EXT4 | 6a82 | Wrong parameters - File not found |
| MF/DF.SYSTEM/EF.CHV1 | 6982 | Command not allowed - Security status not satisfied |
| MF/DF.SYSTEM/EF.CHV2 | 6982 | Command not allowed - Security status not satisfied |
| MF/DF.SYSTEM/EF.ADM1 | 6982 | Command not allowed - Security status not satisfied |
| MF/DF.SYSTEM/EF.ADM2 | 6982 | Command not allowed - Security status not satisfied |
| MF/DF.SYSTEM/EF.ADM3 | 6a82 | Wrong parameters - File not found |
| MF/DF.SYSTEM/EF.ADM4 | 6a82 | Wrong parameters - File not found |
| MF/DF.SYSTEM/EF.SIM_AUTH_COUNTER | 6a82 | Wrong parameters - File not found |
| MF/ADF.USIM/EF.EXT4 | 6a82 | Wrong parameters - File not found |
| MF/ADF.USIM/EF.RPLMNAcTD | 6a82 | Wrong parameters - File not found |
| MF/ADF.USIM/EF.EHPLMN | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/EF.EHPLMNPI | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/EF.IMSConfigData | 6a82 | Wrong parameters - File not found |
| MF/ADF.USIM/EF.XCAPConfigData | 6a82 | Wrong parameters - File not found |
| MF/ADF.USIM/EF.MuDMiDConfigData | 6a82 | Wrong parameters - File not found |
| MF/ADF.USIM/EF.GBAUAPI | 6a82 | Wrong parameters - File not found |
| MF/ADF.USIM/EF.IMSDCI | 6a82 | Wrong parameters - File not found |
| MF/ADF.USIM/DF.WLAN/EF.UPLMNWLAN | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5GS/EF.CAG | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5GS/EF.SOR-CMCI | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5GS/EF.DRI | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5GS/EF.5GSEDRX | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5GS/EF.5GNSWO_CONF | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5GS/EF.MCHPPLMN | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5GS/EF.KAUSF_DERIVATION | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.SNPN/EF.PWS_SNPN | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.SNPN/EF.NID | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_ST | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_DD | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_DC | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_U2NRU | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_RU | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_UIR | 6984 | Command not allowed - Referenced data invalidated |
| MF/ADF.USIM/EF.GBA_SK | 6982 | Command not allowed - Security status not satisfied |
| MF/ADF.USIM/EF.GBA_REC_LIST | 6982 | Command not allowed - Security status not satisfied |
| MF/ADF.USIM/EF.GBA_INT_KEY | 6982 | Command not allowed - Security status not satisfied |
| MF/ADF.ISIM/EF.SMS | 6a82 | Wrong parameters - File not found |
| MF/ADF.ISIM/EF.SMSS | 6a82 | Wrong parameters - File not found |
| MF/ADF.ISIM/EF.SMSR | 6a82 | Wrong parameters - File not found |
| MF/ADF.ISIM/EF.SMSP | 6a82 | Wrong parameters - File not found |

## Decoder limitations

The following byte reads succeeded but offline decoding failed. Their raw contents are retained in the appendix. Padded records can also decode into sentinel/default values; interpret all-ff fields as unconfigured rather than literal network settings.

| Path | Decoder error |
| --- | --- |
| MF/ADF.USIM/DF.5GS/EF.SUCI_Calc_Info | object of type 'NoneType' has no len() |
| MF/ADF.USIM/DF.5GS/EF.SUPI_NAI | cannot unpack non-iterable NoneType object |
| MF/ADF.USIM/DF.SAIP/EF.SUCI_Calc_Info | object of type 'NoneType' has no len() |

## Complete recorded file inventory

Paths are pySIM logical paths. FIDs, sizes, structures and lifecycle values below come from SELECT responses where available. Contents-read means the raw read succeeded; sensitive values can still be omitted from this document.

| Path | FID | Allocation | Lifecycle | Result |
| --- | --- | --- | --- | --- |
| MF | 3f00 | directory | operational_activated | selected directory |
| MF/DF.GSM | 7f20 | directory | operational_activated | selected directory |
| MF/DF.GSM/EF.LP | 6f05 | 5 B | operational_activated | read |
| MF/DF.GSM/EF.IMSI | 6f07 | 9 B | operational_activated | read |
| MF/DF.GSM/EF.Kc | 6f20 | 9 B | operational_activated | read; values omitted |
| MF/DF.GSM/EF.PLMNsel | 6f30 | 60 B | operational_activated | read |
| MF/DF.GSM/EF.HPPLMN | 6f31 | 1 B | operational_activated | read |
| MF/DF.GSM/EF.ACMmax | 6f37 | 3 B | operational_activated | read |
| MF/DF.GSM/EF.SST | 6f38 | 15 B | operational_activated | read |
| MF/DF.GSM/EF.ACM | 6f39 | 20 × 3 B | operational_activated | read |
| MF/DF.GSM/EF.GID1 | 6f3e | 10 B | operational_activated | read |
| MF/DF.GSM/EF.GID2 | 6f3f | 10 B | operational_activated | read |
| MF/DF.GSM/EF.SPN | 6f46 | 17 B | operational_activated | read |
| MF/DF.GSM/EF.PUCT | 6f41 | 5 B | operational_activated | read |
| MF/DF.GSM/EF.CBMI | 6f45 | 40 B | operational_activated | read |
| MF/DF.GSM/EF.BCCH | 6f74 | 16 B | operational_activated | read |
| MF/DF.GSM/EF.ACC | 6f78 | 2 B | operational_activated | read |
| MF/DF.GSM/EF.FPLMN | 6f7b | 12 B | operational_activated | read |
| MF/DF.GSM/EF.LOCI | 6f7e | 11 B | operational_activated | read |
| MF/DF.GSM/EF.AD | 6fad | 4 B | operational_activated | read |
| MF/DF.GSM/EF.Phase | 6fae | 1 B | operational_activated | read |
| MF/DF.GSM/EF.VGCS | 6fb1 | 200 B | operational_activated | read |
| MF/DF.GSM/EF.VGCSS | 6fb2 | 7 B | operational_activated | read |
| MF/DF.GSM/EF.VBS | 6fb3 | 200 B | operational_activated | read |
| MF/DF.GSM/EF.VBSS | 6fb4 | 7 B | operational_activated | read |
| MF/DF.GSM/EF.eMLPP | 6fb5 | 2 B | operational_activated | read |
| MF/DF.GSM/EF.AAeM | 6fb6 | 1 B | operational_activated | read |
| MF/DF.GSM/EF.CBMID | 6f48 | 20 B | operational_activated | read |
| MF/DF.GSM/EF.ECC | 6fb7 | 15 B | operational_activated | read |
| MF/DF.GSM/EF.CBMIR | 6f50 | 20 B | operational_activated | read |
| MF/DF.GSM/EF.DCK | 6f2c | 16 B | operational_activated | read |
| MF/DF.GSM/EF.CNL | 6f32 | 24 B | operational_activated | read |
| MF/DF.GSM/EF.NIA | 6f51 | 5 × 21 B | operational_activated | read |
| MF/DF.GSM/EF.KcGPRS | 6f52 | 9 B | operational_activated | read; values omitted |
| MF/DF.GSM/EF.LOCIGPRS | 6f53 | 14 B | operational_activated | read |
| MF/DF.GSM/EF.SUME | 6f54 | 21 B | operational_activated | read |
| MF/DF.GSM/EF.PLMNwAcT | 6f60 | 60 B | operational_activated | read |
| MF/DF.GSM/EF.OPLMNwAcT | 6f61 | 60 B | operational_activated | read |
| MF/DF.GSM/EF.HPLMNwAcT | 6f62 | 60 B | operational_activated | read |
| MF/DF.GSM/EF.CPBCCH | — | — | — | 6a82 |
| MF/DF.GSM/EF.InvScan | 6f64 | 1 B | operational_activated | read |
| MF/DF.GSM/EF.PNN | 6fc5 | 10 × 24 B | operational_activated | read |
| MF/DF.GSM/EF.OPL | 6fc6 | 2 × 8 B | operational_activated | read |
| MF/DF.GSM/EF.MBDN | 6fc7 | 10 × 24 B | operational_activated | read |
| MF/DF.GSM/EF.MBI | 6fc9 | 10 × 4 B | operational_activated | read |
| MF/DF.GSM/EF.MWIS | 6fca | 4 × 5 B | operational_activated | read |
| MF/DF.GSM/EF.CFIS | 6fcb | 4 × 16 B | operational_activated | read |
| MF/DF.GSM/EF.EXT6 | 6fc8 | 10 × 13 B | operational_activated | read |
| MF/DF.GSM/EF.EXT7 | 6fcc | 4 × 13 B | operational_activated | read |
| MF/DF.GSM/EF.SPDI | 6fcd | 33 B | operational_activated | read |
| MF/DF.GSM/EF.MMSN | 6fce | 4 × 24 B | operational_activated | read |
| MF/DF.GSM/EF.EXT8 | 6fcf | 4 × 64 B | operational_activated | read |
| MF/DF.GSM/EF.MMSICP | 6fd0 | 32 B | operational_activated | read |
| MF/DF.GSM/EF.MMSUP | 6fd1 | 4 × 64 B | operational_activated | read |
| MF/DF.GSM/EF.MMSUCP | 6fd2 | 256 B | operational_activated | read |
| MF/DF.TELECOM | 7f10 | directory | operational_activated | selected directory |
| MF/DF.TELECOM/EF.ADN | 6f3a | 250 × 34 B | operational_activated | read |
| MF/DF.TELECOM/EF.FDN | 6f3b | 20 × 28 B | operational_activated | read |
| MF/DF.TELECOM/EF.SMS | 6f3c | 30 × 176 B | operational_activated | read |
| MF/DF.TELECOM/EF.CCP | — | — | — | 6a82 |
| MF/DF.TELECOM/EF.ECCP | 6f4f | 20 × 15 B | operational_activated | read |
| MF/DF.TELECOM/EF.MSISDN | 6f40 | 6 × 34 B | operational_activated | read |
| MF/DF.TELECOM/EF.SMSP | 6f42 | 2 × 52 B | operational_activated | read |
| MF/DF.TELECOM/EF.SMSS | 6f43 | 2 B | operational_activated | read |
| MF/DF.TELECOM/EF.LND | 6f44 | 20 × 34 B | operational_activated | read |
| MF/DF.TELECOM/EF.SDN | 6f49 | 20 × 34 B | operational_activated | read |
| MF/DF.TELECOM/EF.EXT1 | 6f4a | 10 × 13 B | operational_activated | read |
| MF/DF.TELECOM/EF.EXT2 | 6f4b | 16 × 13 B | operational_activated | read |
| MF/DF.TELECOM/EF.EXT3 | 6f4c | 16 × 13 B | operational_activated | read |
| MF/DF.TELECOM/EF.BDN | 6f4d | 10 × 29 B | operational_activated | read |
| MF/DF.TELECOM/EF.EXT4 | — | — | — | 6a82 |
| MF/DF.TELECOM/EF.SMSR | 6f47 | 20 × 30 B | operational_activated | read |
| MF/DF.TELECOM/EF.CMI | 6f58 | 10 × 11 B | operational_activated | read |
| MF/DF.TELECOM/DF.PHONEBOOK | 5f3a | directory | operational_activated | selected directory |
| MF/DF.TELECOM/DF.PHONEBOOK/EF.PBR | 4f30 | 1 × 69 B | operational_activated | read |
| MF/DF.TELECOM/DF.PHONEBOOK/EF.PSC | 4f22 | 4 B | operational_activated | read |
| MF/DF.TELECOM/DF.PHONEBOOK/EF.CC | 4f23 | 2 B | operational_activated | read |
| MF/DF.TELECOM/DF.PHONEBOOK/EF.PUID | 4f24 | 2 B | operational_activated | read |
| MF/DF.TELECOM/DF.MCS | 5f3d | directory | operational_activated | selected directory |
| MF/DF.TELECOM/DF.MCS/EF.MST | 4f01 | 4 B | operational_activated | read |
| MF/DF.TELECOM/DF.MCS/EF.MCS_CONFIG | 4f02 | 0 B (BER-TLV) | operational_activated | read |
| MF/DF.TELECOM/DF.V2X | 5f3e | directory | operational_activated | selected directory |
| MF/DF.TELECOM/DF.V2X/EF.VST | 4f01 | 3 B | operational_activated | read |
| MF/DF.TELECOM/DF.V2X/EF.V2X_CONFIG | 4f02 | 0 B (BER-TLV) | operational_activated | read |
| MF/DF.EIRENE | 7fe0 | directory | operational_activated | selected directory |
| MF/DF.EIRENE/EF.FN | 6ff1 | 81 × 9 B | operational_activated | read |
| MF/DF.EIRENE/EF.CallconfC | 6ff2 | 24 B | operational_activated | read |
| MF/DF.EIRENE/EF.CallconfI | 6ff3 | 10 × 21 B | operational_activated | read |
| MF/DF.EIRENE/EF.Shunting | 6ff4 | 8 B | operational_activated | read |
| MF/DF.EIRENE/EF.GsmrPLMN | 6ff5 | 10 × 9 B | operational_activated | read |
| MF/DF.EIRENE/EF.IC | 6f8d | 10 × 7 B | operational_activated | read |
| MF/DF.EIRENE/EF.NW | 6f80 | 10 × 8 B | operational_activated | read |
| MF/DF.EIRENE/EF.CT | 6f8e | 10 × 6 B | operational_activated | read |
| MF/DF.EIRENE/EF.SC | 6f8f | 5 × 6 B | operational_activated | read |
| MF/DF.EIRENE/EF.FC | 6f88 | 101 × 3 B | operational_activated | read |
| MF/DF.EIRENE/EF.Service | 6f89 | 10 × 10 B | operational_activated | read |
| MF/DF.EIRENE/EF.Call | 6f8a | 10 × 10 B | operational_activated | read |
| MF/DF.EIRENE/EF.FctTeam | 6f8b | 15 × 10 B | operational_activated | read |
| MF/DF.EIRENE/EF.Controller | 6f92 | 10 × 10 B | operational_activated | read |
| MF/DF.EIRENE/EF.Gateway | 6f8c | 10 × 10 B | operational_activated | read |
| MF/DF.EIRENE/EF.5to8digits | 6f81 | 4 B | operational_activated | read |
| MF/DF.EIRENE/EF.2digits | 6f82 | 4 B | operational_activated | read |
| MF/DF.EIRENE/EF.8digits | 6f83 | 4 B | operational_activated | read |
| MF/DF.EIRENE/EF.9digits | 6f84 | 4 B | operational_activated | read |
| MF/DF.EIRENE/EF.SSSSS | 6f85 | 4 B | operational_activated | read |
| MF/DF.EIRENE/EF.LLLLL | 6f86 | 4 B | operational_activated | read |
| MF/DF.EIRENE/EF.Location | 6f91 | 4 B | operational_activated | read |
| MF/DF.EIRENE/EF.FreeNumber | 6f87 | 4 B | operational_activated | read |
| MF/DF.CDMA | 7f25 | directory | operational_activated | selected directory |
| MF/DF.CDMA/EF.CST | 6f32 | 12 B | operational_activated | read |
| MF/DF.CDMA/EF.SPN | 6f41 | 35 B | operational_activated | read |
| MF/DF.CDMA/EF.AD | 6f43 | 3 B | operational_activated | read |
| MF/DF.CDMA/EF.SMS | 6f3c | 30 × 255 B | operational_activated | read |
| MF/EF.DIR | 2f00 | 8 × 43 B | operational_activated | read |
| MF/EF.ICCID | 2fe2 | 10 B | operational_activated | read |
| MF/EF.PL | 2f05 | 10 B | operational_activated | read |
| MF/EF.ARR | 2f06 | 5 × 110 B | operational_activated | read |
| MF/EF.UMPC | 2f08 | 5 B | operational_activated | read |
| MF/DF.SYSTEM | a515 | directory | operational_activated | selected directory |
| MF/DF.SYSTEM/EF.CHV1 | 6f01 | 21 B | operational_activated | 6982 |
| MF/DF.SYSTEM/EF.CHV2 | 6f81 | 21 B | operational_activated | 6982 |
| MF/DF.SYSTEM/EF.ADM1 | 6f0a | 11 B | operational_activated | 6982 |
| MF/DF.SYSTEM/EF.ADM2 | 6f0b | 11 B | operational_activated | 6982 |
| MF/DF.SYSTEM/EF.ADM3 | — | — | — | 6a82 |
| MF/DF.SYSTEM/EF.ADM4 | — | — | — | 6a82 |
| MF/DF.SYSTEM/EF.MILENAGE_CFG | 6f21 | 85 B | operational_activated | read |
| MF/DF.SYSTEM/EF.0348_KEY | 6f22 | 12 × 35 B | operational_activated | read; values omitted |
| MF/DF.SYSTEM/EF.SIM_AUTH_COUNTER | — | — | — | 6a82 |
| MF/DF.SYSTEM/EF.SIM_AUTH_KEY | 6f20 | 33 B | operational_activated | read; values omitted |
| MF/DF.SYSTEM/EF.0348_COUNT | 6f23 | 4 × 7 B | operational_activated | read; values omitted |
| MF/DF.SYSTEM/EF.GP_COUNT | 6f26 | 3 × 5 B | operational_activated | read; values omitted |
| MF/DF.SYSTEM/EF.GP_DIV_DATA | 6f27 | 1 × 12 B | operational_activated | read; values omitted |
| MF/ADF.USIM | — | directory | operational_activated | selected directory |
| MF/ADF.USIM/EF.LI | 6f05 | 10 B | operational_activated | read |
| MF/ADF.USIM/EF.Keys | 6f08 | 33 B | operational_activated | read; values omitted |
| MF/ADF.USIM/EF.KeysPS | 6f09 | 33 B | operational_activated | read; values omitted |
| MF/ADF.USIM/EF.PLMNwAcT | 6f60 | 60 B | operational_activated | read |
| MF/ADF.USIM/EF.HPPLMN | 6f31 | 1 B | operational_activated | read |
| MF/ADF.USIM/EF.ACMmax | 6f37 | 3 B | operational_activated | read |
| MF/ADF.USIM/EF.UST | 6f38 | 20 B | operational_activated | read |
| MF/ADF.USIM/EF.ACM | 6f39 | 20 × 3 B | operational_activated | read |
| MF/ADF.USIM/EF.GID1 | 6f3e | 10 B | operational_activated | read |
| MF/ADF.USIM/EF.GID2 | 6f3f | 10 B | operational_activated | read |
| MF/ADF.USIM/EF.SPN | 6f46 | 17 B | operational_activated | read |
| MF/ADF.USIM/EF.PUCT | 6f41 | 5 B | operational_activated | read |
| MF/ADF.USIM/EF.CBMI | 6f45 | 40 B | operational_activated | read |
| MF/ADF.USIM/EF.ACC | 6f78 | 2 B | operational_activated | read |
| MF/ADF.USIM/EF.FPLMN | 6f7b | 12 B | operational_activated | read |
| MF/ADF.USIM/EF.LOCI | 6f7e | 11 B | operational_activated | read |
| MF/ADF.USIM/EF.AD | 6fad | 5 B | operational_activated | read |
| MF/ADF.USIM/EF.CBMID | 6f48 | 20 B | operational_activated | read |
| MF/ADF.USIM/EF.ECC | 6fb7 | 5 × 18 B | operational_activated | read |
| MF/ADF.USIM/EF.CBMIR | 6f50 | 20 B | operational_activated | read |
| MF/ADF.USIM/EF.PSLOCI | 6f73 | 14 B | operational_activated | read |
| MF/ADF.USIM/EF.FDN | 6f3b | 20 × 28 B | operational_activated | read |
| MF/ADF.USIM/EF.SMS | 6f3c | 30 × 176 B | operational_activated | read |
| MF/ADF.USIM/EF.MSISDN | 6f40 | 6 × 34 B | operational_activated | read |
| MF/ADF.USIM/EF.SMSP | 6f42 | 2 × 52 B | operational_activated | read |
| MF/ADF.USIM/EF.SMSS | 6f43 | 2 B | operational_activated | read |
| MF/ADF.USIM/EF.SDN | 6f49 | 20 × 34 B | operational_activated | read |
| MF/ADF.USIM/EF.EXT2 | 6f4b | 16 × 13 B | operational_activated | read |
| MF/ADF.USIM/EF.EXT3 | 6f4c | 16 × 13 B | operational_activated | read |
| MF/ADF.USIM/EF.SMSR | 6f47 | 20 × 30 B | operational_activated | read |
| MF/ADF.USIM/EF.ICI | 6f80 | 1 × 30 B | operational_activated | read |
| MF/ADF.USIM/EF.OCI | 6f81 | 1 × 30 B | operational_activated | read |
| MF/ADF.USIM/EF.ICT | 6f82 | 1 × 3 B | operational_activated | read |
| MF/ADF.USIM/EF.OCT | 6f83 | 1 × 3 B | operational_activated | read |
| MF/ADF.USIM/EF.EXT5 | 6f4e | 10 × 13 B | operational_activated | read |
| MF/ADF.USIM/EF.CCP2 | 6f4f | 5 × 15 B | operational_activated | read |
| MF/ADF.USIM/EF.eMLPP | 6fb5 | 2 B | operational_activated | read |
| MF/ADF.USIM/EF.AAeM | 6fb6 | 1 B | operational_activated | read |
| MF/ADF.USIM/EF.BDN | 6f4d | 10 × 29 B | operational_activated | read |
| MF/ADF.USIM/EF.EXT4 | — | — | — | 6a82 |
| MF/ADF.USIM/EF.CMI | 6f58 | 10 × 11 B | operational_activated | read |
| MF/ADF.USIM/EF.EST | 6f56 | 9 B | operational_activated | read |
| MF/ADF.USIM/EF.ACL | 6f57 | 256 B | operational_activated | read |
| MF/ADF.USIM/EF.DCK | 6f2c | 16 B | operational_activated | read |
| MF/ADF.USIM/EF.CNL | 6f32 | 24 B | operational_activated | read |
| MF/ADF.USIM/EF.START-HFN | 6f5b | 6 B | operational_activated | read |
| MF/ADF.USIM/EF.THRESHOLD | 6f5c | 3 B | operational_activated | read |
| MF/ADF.USIM/EF.OPLMNwAcT | 6f61 | 60 B | operational_activated | read |
| MF/ADF.USIM/EF.HPLMNwAcT | 6f62 | 60 B | operational_activated | read |
| MF/ADF.USIM/EF.ARR | 6f06 | 12 × 110 B | operational_activated | read |
| MF/ADF.USIM/EF.RPLMNAcTD | — | — | — | 6a82 |
| MF/ADF.USIM/EF.NETPAR | 6fc4 | 64 B | operational_activated | read |
| MF/ADF.USIM/EF.PNN | 6fc5 | 10 × 24 B | operational_activated | read |
| MF/ADF.USIM/EF.OPL | 6fc6 | 2 × 8 B | operational_activated | read |
| MF/ADF.USIM/EF.MBDN | 6fc7 | 10 × 24 B | operational_activated | read |
| MF/ADF.USIM/EF.EXT6 | 6fc8 | 10 × 13 B | operational_activated | read |
| MF/ADF.USIM/EF.MBI | 6fc9 | 10 × 4 B | operational_activated | read |
| MF/ADF.USIM/EF.MWIS | 6fca | 4 × 5 B | operational_activated | read |
| MF/ADF.USIM/EF.CFIS | 6fcb | 4 × 16 B | operational_activated | read |
| MF/ADF.USIM/EF.EXT7 | 6fcc | 4 × 13 B | operational_activated | read |
| MF/ADF.USIM/EF.SPDI | 6fcd | 33 B | operational_activated | read |
| MF/ADF.USIM/EF.MMSN | 6fce | 4 × 24 B | operational_activated | read |
| MF/ADF.USIM/EF.EXT8 | 6fcf | 4 × 64 B | operational_activated | read |
| MF/ADF.USIM/EF.MMSICP | 6fd0 | 32 B | operational_activated | read |
| MF/ADF.USIM/EF.MMSUP | 6fd1 | 4 × 64 B | operational_activated | read |
| MF/ADF.USIM/EF.MMSUCP | 6fd2 | 256 B | operational_activated | read |
| MF/ADF.USIM/EF.NIA | 6fd3 | 4 × 21 B | operational_activated | read |
| MF/ADF.USIM/EF.VGCS | 6fb1 | 200 B | operational_activated | read |
| MF/ADF.USIM/EF.VGCSS | 6fb2 | 7 B | operational_activated | read |
| MF/ADF.USIM/EF.VBS | 6fb3 | 200 B | operational_activated | read |
| MF/ADF.USIM/EF.VBSS | 6fb4 | 7 B | operational_activated | read |
| MF/ADF.USIM/EF.VGCSCA | 6fd4 | 20 B | operational_activated | read |
| MF/ADF.USIM/EF.VBSCA | 6fd5 | 20 B | operational_activated | read |
| MF/ADF.USIM/EF.GBABP | 6fd6 | 64 B | operational_activated | read; values omitted |
| MF/ADF.USIM/EF.MSK | 6fd7 | 10 × 20 B | operational_activated | read |
| MF/ADF.USIM/EF.MUK | 6fd8 | 1 × 40 B | operational_activated | read |
| MF/ADF.USIM/EF.GBANL | 6fda | 2 × 128 B | operational_activated | read |
| MF/ADF.USIM/EF.EHPLMN | 6fd9 | 12 B | operational_deactivated | 6984 |
| MF/ADF.USIM/EF.EHPLMNPI | 6fdb | 1 B | operational_deactivated | 6984 |
| MF/ADF.USIM/EF.NAFKCA | 6fdd | 2 × 32 B | operational_activated | read |
| MF/ADF.USIM/EF.SPNI | 6fde | 30 B | operational_activated | read |
| MF/ADF.USIM/EF.PNNI | 6fdf | 3 × 30 B | operational_activated | read |
| MF/ADF.USIM/EF.NCP-IP | 6fe2 | 3 × 100 B | operational_activated | read |
| MF/ADF.USIM/EF.EPSLOCI | 6fe3 | 18 B | operational_activated | read |
| MF/ADF.USIM/EF.EPSNSC | 6fe4 | 1 × 100 B | operational_activated | read; values omitted |
| MF/ADF.USIM/EF.UFC | 6fe6 | 64 B | operational_activated | read |
| MF/ADF.USIM/EF.NASCONFIG | 6fe8 | 128 B | operational_activated | read |
| MF/ADF.USIM/EF.PWS | 6fec | 3 B | operational_activated | read |
| MF/ADF.USIM/EF.FDNURI | 6fed | 10 × 128 B | operational_activated | read |
| MF/ADF.USIM/EF.BDNURI | 6fee | 10 × 128 B | operational_activated | read |
| MF/ADF.USIM/EF.SDNURI | 6fef | 10 × 128 B | operational_activated | read |
| MF/ADF.USIM/EF.IPS | 6ff1 | 5 × 4 B | operational_activated | read |
| MF/ADF.USIM/EF.ePDGId | 6ff3 | 60 B | operational_activated | read |
| MF/ADF.USIM/EF.ePDGSelection | 6ff4 | 21 B | operational_activated | read |
| MF/ADF.USIM/EF.ePDGIdEm | 6ff5 | 60 B | operational_activated | read |
| MF/ADF.USIM/EF.ePDGSelectionEm | 6ff6 | 21 B | operational_activated | read |
| MF/ADF.USIM/EF.FromPreferred | 6ff7 | 1 B | operational_activated | read |
| MF/ADF.USIM/EF.IMSConfigData | — | — | — | 6a82 |
| MF/ADF.USIM/EF.XCAPConfigData | — | — | — | 6a82 |
| MF/ADF.USIM/EF.EARFCNList | 6ffd | 128 B | operational_activated | read |
| MF/ADF.USIM/EF.MuDMiDConfigData | — | — | — | 6a82 |
| MF/ADF.USIM/EF.eAKA | 6f01 | 1 B | operational_activated | read |
| MF/ADF.USIM/EF.OCST | 6f02 | 100 B | operational_activated | read |
| MF/ADF.USIM/EF.GBAUAPI | — | — | — | 6a82 |
| MF/ADF.USIM/EF.IMSDCI | — | — | — | 6a82 |
| MF/ADF.USIM/DF.GSM-ACCESS | 5f3b | directory | operational_activated | selected directory |
| MF/ADF.USIM/DF.GSM-ACCESS/EF.Kc | 4f20 | 9 B | operational_activated | read; values omitted |
| MF/ADF.USIM/DF.GSM-ACCESS/EF.KcGPRS | 4f52 | 9 B | operational_activated | read; values omitted |
| MF/ADF.USIM/DF.GSM-ACCESS/EF.CPBCCH | 4f63 | 16 B | operational_activated | read |
| MF/ADF.USIM/DF.GSM-ACCESS/EF.InvScan | 4f64 | 1 B | operational_activated | read |
| MF/ADF.USIM/DF.WLAN | 5f40 | directory | operational_activated | selected directory |
| MF/ADF.USIM/DF.WLAN/EF.Pseudo | 4f41 | 20 B | operational_activated | read |
| MF/ADF.USIM/DF.WLAN/EF.UPLMNWLAN | 4f42 | 60 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.WLAN/EF.OPLMNWLAN | 4f43 | 60 B | operational_activated | read |
| MF/ADF.USIM/DF.WLAN/EF.UWSIDL | 4f44 | 10 × 33 B | operational_activated | read |
| MF/ADF.USIM/DF.WLAN/EF.OWSIDL | 4f45 | 10 × 33 B | operational_activated | read |
| MF/ADF.USIM/DF.WLAN/EF.WRI | 4f46 | 100 B | operational_activated | read |
| MF/ADF.USIM/DF.WLAN/EF.HWSIDL | 4f47 | 10 × 33 B | operational_activated | read |
| MF/ADF.USIM/DF.WLAN/EF.WEHPLMNPI | 4f48 | 1 B | operational_activated | read |
| MF/ADF.USIM/DF.WLAN/EF.WHPI | 4f49 | 1 B | operational_activated | read |
| MF/ADF.USIM/DF.WLAN/EF.WLRPLMN | 4f4a | 3 B | operational_activated | read |
| MF/ADF.USIM/DF.WLAN/EF.HPLMNDAI | 4f4b | 1 B | operational_activated | read |
| MF/ADF.USIM/DF.HNB | 5f50 | directory | operational_activated | selected directory |
| MF/ADF.USIM/DF.HNB/EF.ACSGL | 4f81 | 1 × 50 B | operational_activated | read |
| MF/ADF.USIM/DF.HNB/EF.CSGT | 4f82 | 1 × 30 B | operational_activated | read |
| MF/ADF.USIM/DF.HNB/EF.HNBN | 4f83 | 1 × 30 B | operational_activated | read |
| MF/ADF.USIM/DF.HNB/EF.OCSGL | 4f84 | 1 × 50 B | operational_activated | read |
| MF/ADF.USIM/DF.HNB/EF.OCSGT | 4f85 | 1 × 30 B | operational_activated | read |
| MF/ADF.USIM/DF.HNB/EF.OHNBN | 4f86 | 1 × 30 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe | 5f90 | directory | operational_activated | selected directory |
| MF/ADF.USIM/DF.ProSe/EF.PROSE_MON | 4f01 | 3 × 50 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PROSE_ANN | 4f02 | 3 × 50 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PROSEFUNC | 4f03 | 1 × 25 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PROSE_RADIO_COM | 4f04 | 1 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PROSE_RADIO_MON | 4f05 | 50 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PROSE_RADIO_ANN | 4f06 | 50 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PROSE_POLICY | 4f07 | 3 × 50 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PROSE_PLMN | 4f08 | 3 × 25 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PROSE_GC | 4f09 | 50 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PST | 4f10 | 3 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.UIRC | 4f11 | 50 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PROSE_GM_DISCOVERY | 4f12 | 3 × 50 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PROSE_RELAY | 4f13 | 3 × 50 B | operational_activated | read |
| MF/ADF.USIM/DF.ProSe/EF.PROSE_RELAY_DISCOVERY | 4f14 | 50 B | operational_activated | read |
| MF/ADF.USIM/DF.5GS | 5fc0 | directory | operational_activated | selected directory |
| MF/ADF.USIM/DF.5GS/EF.5GS3GPPLOCI | 4f01 | 20 B | operational_activated | read |
| MF/ADF.USIM/DF.5GS/EF.5GSN3GPPLOCI | 4f02 | 20 B | operational_activated | read |
| MF/ADF.USIM/DF.5GS/EF.5GS3GPPNSC | 4f03 | 1 × 64 B | operational_activated | read; values omitted |
| MF/ADF.USIM/DF.5GS/EF.5GSN3GPPNSC | 4f04 | 1 × 64 B | operational_activated | read; values omitted |
| MF/ADF.USIM/DF.5GS/EF.5GAUTHKEYS | 4f05 | 110 B | operational_activated | read; values omitted |
| MF/ADF.USIM/DF.5GS/EF.UAC_AIC | 4f06 | 4 B | operational_activated | read |
| MF/ADF.USIM/DF.5GS/EF.SUCI_Calc_Info | 4f07 | 200 B | operational_activated | read |
| MF/ADF.USIM/DF.5GS/EF.OPL5G | 4f08 | 10 × 10 B | operational_activated | read |
| MF/ADF.USIM/DF.5GS/EF.SUPI_NAI | 4f09 | 200 B | operational_activated | read |
| MF/ADF.USIM/DF.5GS/EF.Routing_Indicator | 4f0a | 4 B | operational_activated | read |
| MF/ADF.USIM/DF.5GS/EF.URSP | 4f0b | 200 B | operational_activated | read |
| MF/ADF.USIM/DF.5GS/EF.TN3GPPSNN | 4f0c | 200 B | operational_activated | read |
| MF/ADF.USIM/DF.5GS/EF.CAG | 4f0d | 100 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5GS/EF.SOR-CMCI | 4f0e | 100 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5GS/EF.DRI | 4f0f | 7 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5GS/EF.5GSEDRX | 4f10 | 2 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5GS/EF.5GNSWO_CONF | 4f11 | 1 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5GS/EF.MCHPPLMN | 4f15 | 1 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5GS/EF.KAUSF_DERIVATION | 4f16 | 1 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.SNPN | 5fe0 | directory | operational_activated | selected directory |
| MF/ADF.USIM/DF.SNPN/EF.PWS_SNPN | 4f01 | 1 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.SNPN/EF.NID | 4f02 | 10 × 6 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5G_ProSe | 5ff0 | directory | operational_activated | selected directory |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_ST | 4f01 | 4 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_DD | 4f02 | 32 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_DC | 4f03 | 12 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_U2NRU | 4f04 | 40 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_RU | 4f05 | 36 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_UIR | 4f06 | 40 B | operational_deactivated | 6984 |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_U2URU | 4f07 | 100 B | operational_activated | read |
| MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_EU | 4f08 | 100 B | operational_activated | read |
| MF/ADF.USIM/DF.SAIP | 5fd0 | directory | operational_activated | selected directory |
| MF/ADF.USIM/DF.SAIP/EF.SUCI_Calc_Info | 4f01 | 200 B | operational_activated | read |
| MF/ADF.USIM/DF.5MBSUECONFIG | 5ff1 | directory | operational_activated | selected directory |
| MF/ADF.USIM/DF.5MBSUECONFIG/EF.5MBSUECONFIG | 4f01 | 100 B | operational_activated | read |
| MF/ADF.USIM/EF.IMSI | 6f07 | 9 B | operational_activated | read |
| MF/ADF.USIM/EF.USIM_AUTH_KEY | af20 | 67 B | operational_activated | read; values omitted |
| MF/ADF.USIM/EF.USIM_AUTH_KEY_2G | af22 | 33 B | operational_activated | read; values omitted |
| MF/ADF.USIM/EF.GBA_SK | af31 | 33 B | operational_activated | 6982 |
| MF/ADF.USIM/EF.GBA_REC_LIST | af32 | 200 B | operational_activated | 6982 |
| MF/ADF.USIM/EF.GBA_INT_KEY | af33 | 1 × 32 B | operational_activated | 6982 |
| MF/ADF.USIM/EF.USIM_SQN | af30 | 206 B | operational_activated | read |
| MF/ADF.ISIM | ff02 | directory | operational_activated | selected directory |
| MF/ADF.ISIM/EF.IMPI | 6f02 | 128 B | operational_activated | read |
| MF/ADF.ISIM/EF.DOMAIN | 6f03 | 50 B | operational_activated | read |
| MF/ADF.ISIM/EF.IMPU | 6f04 | 8 × 128 B | operational_activated | read |
| MF/ADF.ISIM/EF.AD | 6fad | 3 B | operational_activated | read |
| MF/ADF.ISIM/EF.ARR | 6f06 | 4 × 50 B | operational_activated | read |
| MF/ADF.ISIM/EF.IST | 6f07 | 3 B | operational_activated | read |
| MF/ADF.ISIM/EF.P-CSCF | 6f09 | 8 × 128 B | operational_activated | read |
| MF/ADF.ISIM/EF.GBABP | 6fd5 | 64 B | operational_activated | read; values omitted |
| MF/ADF.ISIM/EF.GBANL | 6fd7 | 8 × 128 B | operational_activated | read |
| MF/ADF.ISIM/EF.NAFKCA | 6fdd | 8 × 128 B | operational_activated | read |
| MF/ADF.ISIM/EF.SMS | — | — | — | 6a82 |
| MF/ADF.ISIM/EF.SMSS | — | — | — | 6a82 |
| MF/ADF.ISIM/EF.SMSR | — | — | — | 6a82 |
| MF/ADF.ISIM/EF.SMSP | — | — | — | 6a82 |
| MF/ADF.ISIM/EF.UICCIARI | 6fe7 | 8 × 64 B | operational_activated | read |
| MF/ADF.ISIM/EF.FromPreferred | 6ff7 | 1 B | operational_activated | read |
| MF/ADF.ISIM/EF.IMSConfigData | 6ff8 | 0 B (BER-TLV) | operational_activated | read |
| MF/ADF.ISIM/EF.XCAPConfigData | 6ffc | 0 B (BER-TLV) | operational_activated | read |
| MF/ADF.ISIM/EF.WebRTCURI | 6ffa | 10 × 100 B | operational_activated | read |
| MF/ADF.ISIM/EF.MuDMiDConfigData | 6ffe | 0 B (BER-TLV) | operational_activated | read |
| MF/ADF.ISIM/EF.GBAUAPI | 6f0a | 3 × 32 B | operational_activated | read |
| MF/ADF.ISIM/EF.IMSDCI | 6f0b | 1 B | operational_activated | read |
| MF/ADF.ISIM/EF.ISIM_AUTH_KEY | af20 | 67 B | operational_activated | read; values omitted |
| MF/ADF.ISIM/EF.ISIM_AUTH_KEY_2G | af22 | 33 B | operational_activated | read; values omitted |
| MF/ADF.ISIM/EF.ISIM_SQN | af30 | 206 B | operational_activated | read |
| MF/ADF.ISD | — | not reported | — | application entry; no filesystem metadata |

## Raw contents appendix (non-secret files)

Exact hex bytes are retained below with run-length notation: `[ff × N]` means exactly N repetitions of byte ff. Identical records are grouped by their 1-based record numbers. An empty BER-TLV object map means RETRIEVE DATA yielded no stored tags, not a measured zero-byte file allocation. Omitted files remain listed in the inventory above.

### MF/DF.GSM/EF.LP

`ffffffffff`

### MF/DF.GSM/EF.IMSI

`082926100000910200`

### MF/DF.GSM/EF.PLMNsel

`[ff × 60]`

### MF/DF.GSM/EF.HPPLMN

`05`

### MF/DF.GSM/EF.ACMmax

`000000`

### MF/DF.GSM/EF.SST

`ff33ffff3f003f0f300cf0c3f00000`

### MF/DF.GSM/EF.ACM

- Records 1–20: `000000`

### MF/DF.GSM/EF.GID1

`[ff × 10]`

### MF/DF.GSM/EF.GID2

`[ff × 10]`

### MF/DF.GSM/EF.SPN

`00[ff × 16]`

### MF/DF.GSM/EF.PUCT

`ffffff0000`

### MF/DF.GSM/EF.CBMI

`[ff × 40]`

### MF/DF.GSM/EF.BCCH

`[ff × 16]`

### MF/DF.GSM/EF.ACC

`0001`

### MF/DF.GSM/EF.FPLMN

`[ff × 12]`

### MF/DF.GSM/EF.LOCI

`ffffffffffffff0000ff01`

### MF/DF.GSM/EF.AD

`00000002`

### MF/DF.GSM/EF.Phase

`03`

### MF/DF.GSM/EF.VGCS

`[ff × 200]`

### MF/DF.GSM/EF.VGCSS

`ffffffffffffff`

### MF/DF.GSM/EF.VBS

`[ff × 200]`

### MF/DF.GSM/EF.VBSS

`ffffffffffffff`

### MF/DF.GSM/EF.eMLPP

`0000`

### MF/DF.GSM/EF.AAeM

`00`

### MF/DF.GSM/EF.CBMID

`[ff × 20]`

### MF/DF.GSM/EF.ECC

`[ff × 15]`

### MF/DF.GSM/EF.CBMIR

`[ff × 20]`

### MF/DF.GSM/EF.DCK

`[ff × 16]`

### MF/DF.GSM/EF.CNL

`[ff × 24]`

### MF/DF.GSM/EF.NIA

- Records 1–5: `[ff × 21]`

### MF/DF.GSM/EF.LOCIGPRS

`[ff × 9]000000ff01`

### MF/DF.GSM/EF.SUME

`850c53544b205365727669636573ffffffffffffff`

### MF/DF.GSM/EF.PLMNwAcT

`ffffff0000ffffff0000[ff × 48]0000`

### MF/DF.GSM/EF.OPLMNwAcT

`ffffff0000ffffff0000[ff × 48]0000`

### MF/DF.GSM/EF.HPLMNwAcT

`ffffff0000ffffff0000[ff × 48]0000`

### MF/DF.GSM/EF.InvScan

`00`

### MF/DF.GSM/EF.PNN

- Records 1–10: `[ff × 24]`

### MF/DF.GSM/EF.OPL

- Records 1–2: `[ff × 8]`

### MF/DF.GSM/EF.MBDN

- Records 1–10: `[ff × 24]`

### MF/DF.GSM/EF.MBI

- Records 1–10: `ffffffff`

### MF/DF.GSM/EF.MWIS

- Records 1–4: `ffffffffff`

### MF/DF.GSM/EF.CFIS

- Records 1: `0100[ff × 14]`
- Records 2: `0200[ff × 14]`
- Records 3: `0300[ff × 14]`
- Records 4: `0400[ff × 14]`

### MF/DF.GSM/EF.EXT6

- Records 1–10: `[ff × 13]`

### MF/DF.GSM/EF.EXT7

- Records 1–4: `[ff × 13]`

### MF/DF.GSM/EF.SPDI

`[ff × 33]`

### MF/DF.GSM/EF.MMSN

- Records 1–4: `[ff × 24]`

### MF/DF.GSM/EF.EXT8

- Records 1–4: `[ff × 64]`

### MF/DF.GSM/EF.MMSICP

`[ff × 32]`

### MF/DF.GSM/EF.MMSUP

- Records 1–4: `[ff × 64]`

### MF/DF.GSM/EF.MMSUCP

`[ff × 256]`

### MF/DF.TELECOM/EF.ADN

- Records 1–250: `[ff × 34]`

### MF/DF.TELECOM/EF.FDN

- Records 1–20: `[ff × 28]`

### MF/DF.TELECOM/EF.SMS

- Records 1–30: `00[ff × 175]`

### MF/DF.TELECOM/EF.ECCP

- Records 1–20: `[ff × 15]`

### MF/DF.TELECOM/EF.MSISDN

- Records 1–6: `[ff × 34]`

### MF/DF.TELECOM/EF.SMSP

- Records 1: `[ff × 24]e1[ff × 12]06815384090067ffffffffff000000`
- Records 2: `[ff × 52]`

### MF/DF.TELECOM/EF.SMSS

`ffff`

### MF/DF.TELECOM/EF.LND

- Records 1–20: `[ff × 34]`

### MF/DF.TELECOM/EF.SDN

- Records 1–20: `[ff × 34]`

### MF/DF.TELECOM/EF.EXT1

- Records 1–10: `[ff × 13]`

### MF/DF.TELECOM/EF.EXT2

- Records 1–16: `00[ff × 12]`

### MF/DF.TELECOM/EF.EXT3

- Records 1–16: `00[ff × 12]`

### MF/DF.TELECOM/EF.BDN

- Records 1–10: `[ff × 29]`

### MF/DF.TELECOM/EF.SMSR

- Records 1–20: `00[ff × 29]`

### MF/DF.TELECOM/EF.CMI

- Records 1–10: `[ff × 11]`

### MF/DF.TELECOM/DF.PHONEBOOK/EF.PBR

- Records 1: `a81ec0034f3a01c1034f3202c3034f5414c5034f0904c6034f5212c9034f2109a90ac4034f1108ca034f500daa14c2034f4a03c7034f4b06c8034f5313cb034f4f16ffffff`

### MF/DF.TELECOM/DF.PHONEBOOK/EF.PSC

`00000000`

### MF/DF.TELECOM/DF.PHONEBOOK/EF.CC

`0000`

### MF/DF.TELECOM/DF.PHONEBOOK/EF.PUID

`0000`

### MF/DF.TELECOM/DF.MCS/EF.MST

`ffffffff`

### MF/DF.TELECOM/DF.MCS/EF.MCS_CONFIG

```json
{}
```

### MF/DF.TELECOM/DF.V2X/EF.VST

`000000`

### MF/DF.TELECOM/DF.V2X/EF.V2X_CONFIG

```json
{}
```

### MF/DF.EIRENE/EF.FN

- Records 1–81: `[ff × 9]`

### MF/DF.EIRENE/EF.CallconfC

`[ff × 24]`

### MF/DF.EIRENE/EF.CallconfI

- Records 1–10: `[ff × 21]`

### MF/DF.EIRENE/EF.Shunting

`[ff × 8]`

### MF/DF.EIRENE/EF.GsmrPLMN

- Records 1–10: `[ff × 9]`

### MF/DF.EIRENE/EF.IC

- Records 1: `f06f8e30f90001`
- Records 2: `f06f8e30f30002`
- Records 3: `f06f8e40f90003`
- Records 4–10: `ffffffffffffff`

### MF/DF.EIRENE/EF.NW

- Records 1–10: `[ff × 8]`

### MF/DF.EIRENE/EF.CT

- Records 1: `f26f86f0ff00`
- Records 2: `f06f8ff1ff01`
- Records 3: `f26f81f2ff02`
- Records 4: `f26f83f3ff03`
- Records 5: `f26f84f4ff04`
- Records 6: `f16f89f4ff05`
- Records 7: `f26f86f6ff06`
- Records 8: `f26f91f7ff07`
- Records 9: `f26f87f8ff08`
- Records 10: `f16f8cf9ff09`

### MF/DF.EIRENE/EF.SC

- Records 1: `f26f82f2ff1e`
- Records 2: `f26f82f3ff1f`
- Records 3: `f26f82f4ff20`
- Records 4–5: `ffffffffffff`

### MF/DF.EIRENE/EF.FC

- Records 1, 13–101: `ffffff`
- Records 2: `10ff65`
- Records 3: `20ff66`
- Records 4: `30ff67`
- Records 5: `40ff68`
- Records 6: `50ff69`
- Records 7: `60ff6a`
- Records 8: `70ff6b`
- Records 9: `80ff6c`
- Records 10: `01ff6e`
- Records 11: `02ff78`
- Records 12: `16ffa1`

### MF/DF.EIRENE/EF.Service

- Records 1: `f26f85ffffffffffffff`
- Records 2: `f0ffc8ffffffffffffff`
- Records 3: `f1ffc9ffffffffffffff`
- Records 4–10: `[ff × 10]`

### MF/DF.EIRENE/EF.Call

- Records 1: `f26f82ffffffffffffff`
- Records 2: `f2ff2affffffffffffff`
- Records 3: `f3ff2bffffffffffffff`
- Records 4: `f5ff2dffffffffffffff`
- Records 5: `f6ff2effffffffffffff`
- Records 6: `f7ff2fffffffffffffff`
- Records 7–10: `[ff × 10]`

### MF/DF.EIRENE/EF.FctTeam

- Records 1: `f26f82ffffffffffffff`
- Records 2: `05ff0affffffffffffff`
- Records 3: `15ff0bffffffffffffff`
- Records 4: `25ff0cffffffffffffff`
- Records 5: `35ff0dffffffffffffff`
- Records 6: `45ff0effffffffffffff`
- Records 7: `06ff0fffffffffffffff`
- Records 8: `16ff10ffffffffffffff`
- Records 9: `26ff11ffffffffffffff`
- Records 10: `36ff12ffffffffffffff`
- Records 11: `46ff13ffffffffffffff`
- Records 12–15: `[ff × 10]`

### MF/DF.EIRENE/EF.Controller

- Records 1–10: `[ff × 10]`

### MF/DF.EIRENE/EF.Gateway

- Records 1: `f26f87ffffffffffffff`
- Records 2: `00ff14ffffffffffffff`
- Records 3: `10ff15ffffffffffffff`
- Records 4–10: `[ff × 10]`

### MF/DF.EIRENE/EF.5to8digits

`f16f8885`

### MF/DF.EIRENE/EF.2digits

`ffffff22`

### MF/DF.EIRENE/EF.8digits

`f16f8888`

### MF/DF.EIRENE/EF.9digits

`f16f8899`

### MF/DF.EIRENE/EF.SSSSS

`f16f8a55`

### MF/DF.EIRENE/EF.LLLLL

`f16f8b55`

### MF/DF.EIRENE/EF.Location

`f16f9255`

### MF/DF.EIRENE/EF.FreeNumber

`ffffff00`

### MF/DF.CDMA/EF.CST

`cfc3cf3ccfff3c0300000000`

### MF/DF.CDMA/EF.SPN

`010201736d6172746672656e[ff × 23]`

### MF/DF.CDMA/EF.AD

`000000`

### MF/DF.CDMA/EF.SMS

- Records 1–30: `00[ff × 254]`

### MF/EF.DIR

- Records 1: `61294f10a0000000871002ffffffff890709000050055553696d31730ea00c80011781025f608203454150`
- Records 2: `61194f10a0000000871004ffffffff890709000050054953696d31[ff × 16]`
- Records 3–8: `[ff × 43]`

### MF/EF.ICCID

`989444000000910200f6`

### MF/EF.PL

`[ff × 10]`

### MF/EF.ARR

- Records 1: `800101a40683010a950108800106900080016097008401d4a40683010a950108[ff × 78]`
- Records 2: `80010190008001029700800118a40683010a9501088401d4a40683010a950108[ff × 78]`
- Records 3: `800101a40683010195010880011aa40683010a9501088401d4a40683010a950108[ff × 77]`
- Records 4: `800101900080011aa40683010a9501088401d4a40683010a950108[ff × 83]`
- Records 5: `8001019000800102a406830101950108800118a40683010a9501088401d4a40683010a950108[ff × 72]`

### MF/EF.UMPC

`3cff02ffff`

### MF/DF.SYSTEM/EF.MILENAGE_CFG

`4000204060[00 × 31]01[00 × 15]02[00 × 15]04[00 × 15]08`

### MF/ADF.USIM/EF.LI

`[ff × 10]`

### MF/ADF.USIM/EF.PLMNwAcT

`ffffff0000ffffff0000[ff × 48]0000`

### MF/ADF.USIM/EF.HPPLMN

`05`

### MF/ADF.USIM/EF.ACMmax

`000000`

### MF/ADF.USIM/EF.UST

`beff9f9de73e04080000ff730000002600000000`

### MF/ADF.USIM/EF.ACM

- Records 1–20: `000000`

### MF/ADF.USIM/EF.GID1

`[ff × 10]`

### MF/ADF.USIM/EF.GID2

`[ff × 10]`

### MF/ADF.USIM/EF.SPN

`00[ff × 16]`

### MF/ADF.USIM/EF.PUCT

`ffffff0000`

### MF/ADF.USIM/EF.CBMI

`[ff × 40]`

### MF/ADF.USIM/EF.ACC

`0001`

### MF/ADF.USIM/EF.FPLMN

`[ff × 12]`

### MF/ADF.USIM/EF.LOCI

`ffffffffffffff0000ff01`

### MF/ADF.USIM/EF.AD

`01000802ff`

### MF/ADF.USIM/EF.CBMID

`[ff × 20]`

### MF/ADF.USIM/EF.ECC

- Records 1–5: `[ff × 15]00ffff`

### MF/ADF.USIM/EF.CBMIR

`[ff × 20]`

### MF/ADF.USIM/EF.PSLOCI

`[ff × 9]000000ff01`

### MF/ADF.USIM/EF.FDN

- Records 1–20: `[ff × 28]`

### MF/ADF.USIM/EF.SMS

- Records 1–30: `00[ff × 175]`

### MF/ADF.USIM/EF.MSISDN

- Records 1–6: `[ff × 34]`

### MF/ADF.USIM/EF.SMSP

- Records 1: `[ff × 24]e1[ff × 12]06815384090067ffffffffff000000`
- Records 2: `[ff × 52]`

### MF/ADF.USIM/EF.SMSS

`ffff`

### MF/ADF.USIM/EF.SDN

- Records 1–20: `[ff × 34]`

### MF/ADF.USIM/EF.EXT2

- Records 1–16: `00[ff × 12]`

### MF/ADF.USIM/EF.EXT3

- Records 1–16: `00[ff × 12]`

### MF/ADF.USIM/EF.SMSR

- Records 1–20: `00[ff × 29]`

### MF/ADF.USIM/EF.ICI

- Records 1: `[ff × 23]0000000001ffff`

### MF/ADF.USIM/EF.OCI

- Records 1: `[ff × 24]00000001ffff`

### MF/ADF.USIM/EF.ICT

- Records 1: `000000`

### MF/ADF.USIM/EF.OCT

- Records 1: `000000`

### MF/ADF.USIM/EF.EXT5

- Records 1–10: `00[ff × 12]`

### MF/ADF.USIM/EF.CCP2

- Records 1–5: `[ff × 15]`

### MF/ADF.USIM/EF.eMLPP

`0000`

### MF/ADF.USIM/EF.AAeM

`00`

### MF/ADF.USIM/EF.BDN

- Records 1–10: `[ff × 29]`

### MF/ADF.USIM/EF.CMI

- Records 1–10: `[ff × 11]`

### MF/ADF.USIM/EF.EST

`[00 × 9]`

### MF/ADF.USIM/EF.ACL

`[ff × 256]`

### MF/ADF.USIM/EF.DCK

`[ff × 16]`

### MF/ADF.USIM/EF.CNL

`[ff × 24]`

### MF/ADF.USIM/EF.START-HFN

`f00000f00000`

### MF/ADF.USIM/EF.THRESHOLD

`ffffff`

### MF/ADF.USIM/EF.OPLMNwAcT

`ffffff0000ffffff0000[ff × 48]0000`

### MF/ADF.USIM/EF.HPLMNwAcT

`ffffff0000ffffff0000[ff × 48]0000`

### MF/ADF.USIM/EF.ARR

- Records 1: `8001079000800160a4068301019501088401d4a40683010a950108[ff × 83]`
- Records 2: `8001019000800102a406830101950108800118a40683010a9501088401d4a40683010a950108[ff × 72]`
- Records 3: `800101a40683010195010880011aa40683010a9501088401d4a40683010a950108[ff × 77]`
- Records 4: `800103a406830101950108800118a40683010a9501088401d4a40683010a950108[ff × 77]`
- Records 5: `840132a406830101950108800101a406830101950108800102a406830181950108800118a40683010a95010880012097008401d4a40683010a950108[ff × 50]`
- Records 6: `800101900080011aa40683010a9501088401d4a40683010a950108[ff × 83]`
- Records 7: `800101a406830101950108800102a406830181950108800118a40683010a9501088401d4a40683010a950108[ff × 66]`
- Records 8: `840132a406830101950108800103a406830101950108800118a40683010a9501088401d4a40683010a950108[ff × 66]`
- Records 9: `800101a40683010a950108800102a40683010a950108800110a40683010a950108800108a40683010a950108[ff × 66]`
- Records 10–12: `[ff × 110]`

### MF/ADF.USIM/EF.NETPAR

`[ff × 64]`

### MF/ADF.USIM/EF.PNN

- Records 1–10: `[ff × 24]`

### MF/ADF.USIM/EF.OPL

- Records 1–2: `[ff × 8]`

### MF/ADF.USIM/EF.MBDN

- Records 1–10: `[ff × 24]`

### MF/ADF.USIM/EF.EXT6

- Records 1–10: `[ff × 13]`

### MF/ADF.USIM/EF.MBI

- Records 1–10: `ffffffff`

### MF/ADF.USIM/EF.MWIS

- Records 1–4: `ffffffffff`

### MF/ADF.USIM/EF.CFIS

- Records 1: `0100[ff × 14]`
- Records 2: `0200[ff × 14]`
- Records 3: `0300[ff × 14]`
- Records 4: `0400[ff × 14]`

### MF/ADF.USIM/EF.EXT7

- Records 1–4: `[ff × 13]`

### MF/ADF.USIM/EF.SPDI

`[ff × 33]`

### MF/ADF.USIM/EF.MMSN

- Records 1–4: `[ff × 24]`

### MF/ADF.USIM/EF.EXT8

- Records 1–4: `[ff × 64]`

### MF/ADF.USIM/EF.MMSICP

`[ff × 32]`

### MF/ADF.USIM/EF.MMSUP

- Records 1–4: `[ff × 64]`

### MF/ADF.USIM/EF.MMSUCP

`[ff × 256]`

### MF/ADF.USIM/EF.NIA

- Records 1–4: `[ff × 21]`

### MF/ADF.USIM/EF.VGCS

`[ff × 200]`

### MF/ADF.USIM/EF.VGCSS

`ffffffffffffff`

### MF/ADF.USIM/EF.VBS

`[ff × 200]`

### MF/ADF.USIM/EF.VBSS

`ffffffffffffff`

### MF/ADF.USIM/EF.VGCSCA

`[00 × 20]`

### MF/ADF.USIM/EF.VBSCA

`[00 × 20]`

### MF/ADF.USIM/EF.MSK

- Records 1–10: `[ff × 20]`

### MF/ADF.USIM/EF.MUK

- Records 1: `[ff × 40]`

### MF/ADF.USIM/EF.GBANL

- Records 1–2: `[ff × 128]`

### MF/ADF.USIM/EF.NAFKCA

- Records 1–2: `[ff × 32]`

### MF/ADF.USIM/EF.SPNI

`[ff × 30]`

### MF/ADF.USIM/EF.PNNI

- Records 1–3: `[ff × 30]`

### MF/ADF.USIM/EF.NCP-IP

- Records 1–3: `[ff × 100]`

### MF/ADF.USIM/EF.EPSLOCI

`[ff × 15]000001`

### MF/ADF.USIM/EF.UFC

`[00 × 64]`

### MF/ADF.USIM/EF.NASCONFIG

`[ff × 128]`

### MF/ADF.USIM/EF.PWS

`000000`

### MF/ADF.USIM/EF.FDNURI

- Records 1–10: `[ff × 128]`

### MF/ADF.USIM/EF.BDNURI

- Records 1–10: `[ff × 128]`

### MF/ADF.USIM/EF.SDNURI

- Records 1–10: `[ff × 128]`

### MF/ADF.USIM/EF.IPS

- Records 1–5: `ffffffff`

### MF/ADF.USIM/EF.ePDGId

`[ff × 60]`

### MF/ADF.USIM/EF.ePDGSelection

`[ff × 21]`

### MF/ADF.USIM/EF.ePDGIdEm

`[ff × 60]`

### MF/ADF.USIM/EF.ePDGSelectionEm

`[ff × 21]`

### MF/ADF.USIM/EF.FromPreferred

`ff`

### MF/ADF.USIM/EF.EARFCNList

`[ff × 128]`

### MF/ADF.USIM/EF.eAKA

`00`

### MF/ADF.USIM/EF.OCST

`00[ff × 99]`

### MF/ADF.USIM/DF.GSM-ACCESS/EF.CPBCCH

`[ff × 16]`

### MF/ADF.USIM/DF.GSM-ACCESS/EF.InvScan

`00`

### MF/ADF.USIM/DF.WLAN/EF.Pseudo

`[ff × 20]`

### MF/ADF.USIM/DF.WLAN/EF.OPLMNWLAN

`[ff × 60]`

### MF/ADF.USIM/DF.WLAN/EF.UWSIDL

- Records 1–10: `[ff × 33]`

### MF/ADF.USIM/DF.WLAN/EF.OWSIDL

- Records 1–10: `[ff × 33]`

### MF/ADF.USIM/DF.WLAN/EF.WRI

`[ff × 100]`

### MF/ADF.USIM/DF.WLAN/EF.HWSIDL

- Records 1–10: `[ff × 33]`

### MF/ADF.USIM/DF.WLAN/EF.WEHPLMNPI

`02`

### MF/ADF.USIM/DF.WLAN/EF.WHPI

`00`

### MF/ADF.USIM/DF.WLAN/EF.WLRPLMN

`ffffff`

### MF/ADF.USIM/DF.WLAN/EF.HPLMNDAI

`01`

### MF/ADF.USIM/DF.HNB/EF.ACSGL

- Records 1: `[ff × 50]`

### MF/ADF.USIM/DF.HNB/EF.CSGT

- Records 1: `[ff × 30]`

### MF/ADF.USIM/DF.HNB/EF.HNBN

- Records 1: `[ff × 30]`

### MF/ADF.USIM/DF.HNB/EF.OCSGL

- Records 1: `[ff × 50]`

### MF/ADF.USIM/DF.HNB/EF.OCSGT

- Records 1: `[ff × 30]`

### MF/ADF.USIM/DF.HNB/EF.OHNBN

- Records 1: `[ff × 30]`

### MF/ADF.USIM/DF.ProSe/EF.PROSE_MON

- Records 1–3: `[ff × 50]`

### MF/ADF.USIM/DF.ProSe/EF.PROSE_ANN

- Records 1–3: `[ff × 50]`

### MF/ADF.USIM/DF.ProSe/EF.PROSEFUNC

- Records 1: `[ff × 25]`

### MF/ADF.USIM/DF.ProSe/EF.PROSE_RADIO_COM

`ff`

### MF/ADF.USIM/DF.ProSe/EF.PROSE_RADIO_MON

`[ff × 50]`

### MF/ADF.USIM/DF.ProSe/EF.PROSE_RADIO_ANN

`[ff × 50]`

### MF/ADF.USIM/DF.ProSe/EF.PROSE_POLICY

- Records 1–3: `[ff × 50]`

### MF/ADF.USIM/DF.ProSe/EF.PROSE_PLMN

- Records 1–3: `[ff × 25]`

### MF/ADF.USIM/DF.ProSe/EF.PROSE_GC

`[ff × 50]`

### MF/ADF.USIM/DF.ProSe/EF.PST

`000000`

### MF/ADF.USIM/DF.ProSe/EF.UIRC

`[ff × 50]`

### MF/ADF.USIM/DF.ProSe/EF.PROSE_GM_DISCOVERY

- Records 1–3: `[ff × 50]`

### MF/ADF.USIM/DF.ProSe/EF.PROSE_RELAY

- Records 1–3: `[ff × 50]`

### MF/ADF.USIM/DF.ProSe/EF.PROSE_RELAY_DISCOVERY

`[ff × 50]`

### MF/ADF.USIM/DF.5GS/EF.5GS3GPPLOCI

`[ff × 19]01`

### MF/ADF.USIM/DF.5GS/EF.5GSN3GPPLOCI

`[ff × 19]01`

### MF/ADF.USIM/DF.5GS/EF.UAC_AIC

`03ffffff`

### MF/ADF.USIM/DF.5GS/EF.SUCI_Calc_Info

`a000[ff × 198]`

### MF/ADF.USIM/DF.5GS/EF.OPL5G

- Records 1–10: `[ff × 10]`

### MF/ADF.USIM/DF.5GS/EF.SUPI_NAI

`[ff × 200]`

### MF/ADF.USIM/DF.5GS/EF.Routing_Indicator

`f0ffffff`

### MF/ADF.USIM/DF.5GS/EF.URSP

`[ff × 200]`

### MF/ADF.USIM/DF.5GS/EF.TN3GPPSNN

`[ff × 200]`

### MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_U2URU

`[ff × 100]`

### MF/ADF.USIM/DF.5G_ProSe/EF.5G_PROSE_EU

`[ff × 100]`

### MF/ADF.USIM/DF.SAIP/EF.SUCI_Calc_Info

`a000[ff × 198]`

### MF/ADF.USIM/DF.5MBSUECONFIG/EF.5MBSUECONFIG

`[ff × 100]`

### MF/ADF.USIM/EF.IMSI

`082926100000910200`

### MF/ADF.USIM/EF.USIM_SQN

`d5030002000000000002[00 × 196]`

### MF/ADF.ISIM/EF.IMPI

`8000[ff × 126]`

### MF/ADF.ISIM/EF.DOMAIN

`8000[ff × 48]`

### MF/ADF.ISIM/EF.IMPU

- Records 1–8: `8000[ff × 126]`

### MF/ADF.ISIM/EF.AD

`ffffff`

### MF/ADF.ISIM/EF.ARR

- Records 1, 4: `800103a406830101950108800118a40683010a9501088401d4a40683010a950108[ff × 17]`
- Records 2: `800101900080011aa40683010a9501088401d4a40683010a950108[ff × 23]`
- Records 3: `800101a40683010195010880011aa40683010a9501088401d4a40683010a950108[ff × 17]`

### MF/ADF.ISIM/EF.IST

`190208`

### MF/ADF.ISIM/EF.P-CSCF

- Records 1–8: `[ff × 128]`

### MF/ADF.ISIM/EF.GBANL

- Records 1–8: `[ff × 128]`

### MF/ADF.ISIM/EF.NAFKCA

- Records 1–8: `[ff × 128]`

### MF/ADF.ISIM/EF.UICCIARI

- Records 1–8: `[ff × 64]`

### MF/ADF.ISIM/EF.FromPreferred

`00`

### MF/ADF.ISIM/EF.IMSConfigData

```json
{}
```

### MF/ADF.ISIM/EF.XCAPConfigData

```json
{}
```

### MF/ADF.ISIM/EF.WebRTCURI

- Records 1–10: `[ff × 100]`

### MF/ADF.ISIM/EF.MuDMiDConfigData

```json
{}
```

### MF/ADF.ISIM/EF.GBAUAPI

- Records 1–3: `[ff × 32]`

### MF/ADF.ISIM/EF.IMSDCI

`ff`

### MF/ADF.ISIM/EF.ISIM_SQN

`d5030002000000000002[00 × 196]`

## Reproducibility and evidence

The report is derived from the successful raw post-ADM filesystem dump, with a separate completed unauthenticated dump for comparison. SHA-256 of the exact raw dump text (including pySIM JSON formatting):

| Evidence | SHA-256 |
| --- | --- |
| raw-complete.txt | ce94371a7c79e8e7cec5e7cc8fcc106dfeaa6570001b69bb4b307a52cb75d6a6 |
| raw-adm.txt | 68e47bc92644b07fb702bb9dd1bf68f7ccc0264b44dc179e54d4beefa319270a |

Temporary acquisition files contained unredacted private card material and were deleted after the report was checked. Their checksums above identify the source snapshots; the non-secret raw file contents are preserved in the appendix. Repository changes were limited to this Markdown report; unrelated pre-existing work was preserved.
