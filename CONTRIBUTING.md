# Contribution Guidelines

When contributing to this repository, please first discuss the changes you wish to make via an issue, email, or any other method, with the owners of this repository before issuing a pull request.

## Community Guidelines

We welcome you to our community! We seek to provide a welcoming and safe development experience for everyone. Please read our [code of conduct](CODE_OF_CONDUCT.md) and reach out to us if you have any questions. We welcome your input!

## How to contribute

### Reporting bugs or making feature requests

To report a bug or suggest a new feature, please go to the [monarch-initiative/monarch-project-template issue tracker](https://github.com/monarch-initiative/monarch-project-template/issues), as we are consolidating issues there.

Please supply enough details to the developers to enable them to verify and troubleshoot your issue:

* Provide a clear and descriptive title as well as a concise summary of the issue to identify the problem.
* Describe the exact steps which reproduce the problem in as many details as possible.
* Describe the behavior you observed after following the steps and point out what exactly is the problem with that behavior.
* Explain which behavior you expected to see instead and why.
* Provide screenshots of the expected or actual behaviour where applicable.


### The development lifecycle

1. Create a bug fix or feature development branch, based off the `main` branch of the upstream repo, and not your fork. Name the branch appropriately, briefly summarizing the bug fix or feature request. If none come to mind, you can include the issue number in the branch name. Some examples of branch names are, `bugfix/breaking-pipfile-error` or `feature/add-click-cli-layer`, or `bugfix/issue-414`
2. Make sure your development branch has all the latest commits from the `main` branch.
3. After completing work and testing locally, push the code to the appropriate branch on your fork or origin repository.
4. Create a pull request from the bug/feature branch of your fork to the `main` branch of the upstream repository.

**NOTE**: All the development must be done on a separate branch, either in your fork or in the origin repository. The `main` branch of the upstream repository should never be used for development.

**ALSO NOTE**: github.com lets you create a pull request from the main branch, automating the steps above.

> A code review (which happens with both the contributor and the reviewer present) is required for contributing.

## Aurelian Philosophy - Simple Python functions all the way!

Currently there are a lot of choices for Agentic frameworks out there. We initially explored smolagents, but we settled on
pydantic-ai due to the awesome developer experience (we still love the idea of CodeAgents with smolagents). We have recently
been exploring the use of mcp, which has nice integration with claude desktop. This led us to try and separate out
the logic of our tools from the framework, and instead 'shim' to mcp and other frameworks.

You'll see that the core of every agent (see [src/aurelian/agents](src/aurelian/agents)) is a simple python package that is a
collection of hopefully useful functions (ideally `async`). These are not totally framework independent, as they
assume a pydantic `RunContext` object, but this is really a generic holder for a domain-specific configuration object.

E.g

 * `foo_tools.py`: simple (mostly async) functions that do useful things in the domain of foo.
 * `foo_mcp.py`: mcp shim layer (could be done completely dynamically in the future?)
 * `foo_agent.py`: basically just a bundle of tools, with system prompt, and maybe default models
 * `foo_gradio.py`: trivial chat UI for the agent, using gradio

In principle langgraph could be added here.

Normal software engineering modularity principles apply. E.g. a highly domain specific agent (phenopackets) could make
use of tools from a more general agent (e.g. monarch), or a very general one (e.g. web search or PMID tools).
With pydantic-ai it's possible to give a bespoke description for a general tool used in the context of an agent.

Of course the world of agents is rapidly evolving, and this may turn out to be a terrible architecture, and
we may end up asking Claude Code to refactor it completely once something else comes along...

But for now, our general philosophy is **simple python functions FTW, mostly async**.

We think this is a good philosophy in general for future engineering in Monarch as a whole. We tend to build
a lot of pipelines, and have gravitated towards Makefiles here for their simplicity, but we all know the limitations.
I think a lot of things (e.g robot build pipelines) might have been better engineered as python async functions
(some calling shell commands, some doing things natively), with lightweight orchestration and task dependency
management, even outside an agentic context.

This is even more important in an agentic context. One of the things we find is the hardest mental barrier for
good developers using agents is the idea of giving up control of how tools chain together - we love to write
pipeline code and have nice well-typed OO constraints on chaining pieces together, but in fact it may be better
to allow for more fluidity and run-time control (whether from an AI or a user, or some kind of dynamic data-driven
pipeline).