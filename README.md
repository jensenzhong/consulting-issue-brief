# Issue Brief Skill

**English** | [简体中文](README.zh-CN.md)

**✨ The issue-organizing skill your boss can't stop praising — turn scattered material into a clear, detailed issue brief.**

Turn issue lists, interview and meeting notes, documents, and weekly reports into a structured brief with the context, scenarios, and evidence its intended readers need.

## When to use it

Use this skill to make sense of fragmented, overlapping, or incomplete material, such as cross-team coordination issues, project retrospectives, operational incidents, or meeting discussion materials. The brief can be written for managers, project teams, business departments, or another audience you specify.

Before organizing the material, the skill establishes **who will read the brief, whose perspective it should use, and what the reader will use it for**. It does not ask again if you have already provided that context. It then adapts the level of detail, terminology, and tone to the audience and keeps them consistent throughout.

By default, the brief focuses on issues, their context, and impacts that have occurred or are ongoing. Ask explicitly if you also want analysis or recommendations. The structure and output format can be adapted to your needs.

## Installation and use

Download or clone this repository into a directory named `consulting-issue-brief`, then add that directory to your AI tool's skills directory according to its documentation. Keep `SKILL.md` and `references/` together. Installation locations and invocation methods vary by tool.

Provide materials you have permission to use, along with the intended audience, writing perspective, and desired output format. For example:

> Organize these interview notes and weekly reports into an issue brief for department heads to discuss at a meeting. Write from the project team's perspective, and describe each issue's context, people involved, available data, and impact. Do not include recommendations.

If your tool supports explicit invocation, specify `consulting-issue-brief` using its syntax. Have someone familiar with the business and source material review the result.

The skill instructions and reference files are currently written in Chinese.

## Files

- [`SKILL.md`](SKILL.md): audience selection, organizing approach, and delivery guidance.
- [`references/item-template.md`](references/item-template.md): a fictional home-appliance manufacturing example.
- [`references/typography.md`](references/typography.md): optional Word formatting guidance.
- [`LICENSE`](LICENSE): MIT License.

## Publishing and privacy

Do not commit client interviews, recordings, reports, registers, completed deliverables, company logos, or other material without authorization to a public repository. `.gitignore` can reduce accidental commits but cannot identify all sensitive information; check file contents, the staging area, and Git history before publishing. Use fictional data in examples.

## License

[MIT License](LICENSE).
