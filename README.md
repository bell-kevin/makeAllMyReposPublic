<a name="readme-top"></a>

# 

 script that flips every repo to public 

 A few things worth knowing before you run it:
 
Token scope. A classic PAT needs the repo scope. A fine-grained PAT needs Administration: Read and write on all your repos. Without sufficient scope, the PATCH returns 403.

Dry run first. I left DRY_RUN = True on purpose. Run it once, eyeball the list, then set it to False. With ~900 repos, you really don't want a typo or a misunderstood filter to surprise you.

Forks are skipped by default. Flip SKIP_FORKS = False if you want them included.

Org repos are excluded. affiliation=owner only returns repos you personally own. If you also want repos in organizations you admin, remove that filter, but then visibility changes may be blocked by org policy.

Irreversible-ish. Making a repo public exposes its full git history, including any secrets ever committed. If you've ever pushed an API key, password, or .env file to a private repo, it'll become world-readable. GitHub also has org/enterprise settings that can block private→public flips, in which case you'll see 422 errors in the output.

--------------------------------------------------------------------------------------------------------------------------

## Automated architecture diagram

This template now includes an automated architecture diagram process:

- `scripts/generate_architecture_diagram.py` scans source files and docs and writes `docs/architecture.mmd`.
- `.github/workflows/update-architecture-diagram.yml` regenerates and commits `docs/architecture.mmd` on every push.
- `.github/workflows/check-architecture-diagram.yml` ensures pull requests have an up-to-date architecture diagram.

### Local usage

```bash
python scripts/generate_architecture_diagram.py
python scripts/generate_architecture_diagram.py --check
```

--------------------------------------------------------------------------------------------------------------------------
== We're Using GitHub Under Protest ==

This project is currently hosted on GitHub.  This is not ideal; GitHub is a
proprietary, trade-secret system that is not Free and Open Souce Software
(FOSS).  We are deeply concerned about using a proprietary system like GitHub
to develop our FOSS project. I have a [website](https://bellKevin.me) where the
project contributors are actively discussing how we can move away from GitHub
in the long term.  We urge you to read about the [Give up GitHub](https://GiveUpGitHub.org) campaign 
from [the Software Freedom Conservancy](https://sfconservancy.org) to understand some of the reasons why GitHub is not 
a good place to host FOSS projects.

If you are a contributor who personally has already quit using GitHub, please
email me at **kevinBell@Linux.com** for how to send us contributions without
using GitHub directly.

Any use of this project's code by GitHub Copilot, past or present, is done
without our permission.  We do not consent to GitHub's use of this project's
code in Copilot.

![Logo of the GiveUpGitHub campaign](https://sfconservancy.org/img/GiveUpGitHub.png)

<p align="right"><a href="#readme-top">back to top</a></p>
