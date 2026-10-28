# Packaging and publishing

This repository includes the source, package builders and marketplace metadata
for distributing Value Pricing. Directory steps are manual; recheck vendor
requirements before each submission because flows and policies can change.

## Build release archives

From the repository root, run:

```sh
sh scripts/package.sh
```

The script writes four archives to the ignored `dist/` directory:

| Archive | Contents and use |
|---|---|
| `value-pricing-skill.zip` | One `value-pricing/` Agent Skill folder for a client that accepts Agent Skills. |
| `value-pricing-plugin.zip` | Claude Code plugin with the skill, council agents and `/value-pricing` command. |
| `value-pricing-codex.zip` | Codex plugin bundle for manual/local installation. |
| `value-pricing-openai.zip` | Portable, skills-only package for the ChatGPT/Codex public plugin directory review flow. |

Archives contain source and sample templates only. They do not include a
customer study, credentials, browser profile, or generated research data. The
analysis scripts need Python 3.11 or later; install the requirements file in a
virtual environment. Browser crawling may additionally require Playwright and
its Chromium browser. See the README for setup details.

## GitHub releases

For a release, update the version in `.claude-plugin/plugin.json`,
`.codex-plugin/plugin.json`, and `plugin.json`, review the README and release
notes, then commit and push. Create and push a matching `vX.Y.Z` tag. The
GitHub Actions workflow builds the archives and attaches them to the release.
Never commit `dist/`; it is generated from the tagged source.

## ClawHub skill (OpenClaw)

The installable artifact is the Agent Skill directory `skills/value-pricing/`; it contains one
`SKILL.md`, references, templates and local Python scripts. Publish it as a **skill**, not as a code
plugin: it has no MCP server or plugin runtime. Before uploading, run the repository self-test and
review ClawHub's security evidence. The skill's crawler restricts requests to public same-origin web
destinations; its self-test refuses to overwrite an existing directory; model calls and the optional API
runner are disclosed in the skill docs.

After the current version is cleared or replaced, users can install the listing with the
ClawHub/OpenClaw skill installer. Confirm the exact command shown by the current OpenClaw release
before publishing instructions.

## Claude plugin directory

The repository is ready for the Claude plugin bundle flow: the Claude plugin
manifest, marketplace manifest, skill, council agents, command, MIT license,
and install guidance are included. Add the public repository as a Claude Code
marketplace with:

```text
/plugin marketplace add C-Kapsalis/value-pricing
/plugin install value-pricing@value-pricing
```

For the public Claude directory, use Claude's plugin submission portal and
select the GitHub repository as the source. The maintainer must provide the
data-handling answers, contact details and compliance acknowledgements in the
portal. Do not infer those answers from the package. Review the current
[Claude plugin directory guidance](https://claude.com/resources/articles/build-plugins-for-claude)
before submission.

## OpenAI plugin directory

Use `dist/value-pricing-openai.zip` in the OpenAI plugin submission portal.
This is a portable, skills-only package and does not include an MCP server or
lifecycle hooks. The package manifest supplies the listing name, description,
category, prompts and icons. The maintainer still needs to verify the identity,
complete any editable listing fields, read and accept the policy attestations,
submit for review, and choose when to publish after approval.

Follow the current
[submission guide](https://developers.openai.com/plugins/deploy/submission)
and [plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines).
The directory is shared by ChatGPT and Codex. Approval is not guaranteed by
passing package validation.

## Skill indexes and personal listings

The repository follows the Agent Skills layout. From OpenClaw, install the
public ClawHub listing with `openclaw skills install @c-kapsalis/value-pricing`
once the security review has cleared. For a local checkout, install
`skills/value-pricing/` directly with `openclaw skills install <path> --as value-pricing`.
Other Agent Skills clients can install with `npx skills add C-Kapsalis/value-pricing`
or download the skill archive from a GitHub release. The skills.sh index is
generated from public GitHub skill repositories; check its current rules before
promoting a listing.

The `.agents/plugins/marketplace.json` file exposes the plugin to Codex's
repository marketplace. Users can add it with:

```sh
codex plugin marketplace add C-Kapsalis/value-pricing
```

The `.claude-plugin/marketplace.json` file exposes the Claude Code plugin to
Claude Code's marketplace command. These GitHub-backed marketplaces are
separate from vendor-reviewed public directories.
