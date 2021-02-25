# Cloudar::CodeBuild::Build

See `docs/README.md` for properties and syntax.

The whole build is considered as one resource.  This means that by default CloudFormation will delete
it from CodeBuild when it is replaced with a new version, or when the build fails. To help with 
debugging it's recommended to add: `DeletionPolicy: Retain` and `UpdateReplacePolicy: Retain` to the
resource.

## Example
There is an example template, `example.yaml`. It will work after you run `cfn submit` to deploy the resource provider in your account (you need docker running to do that).

## Development

- The JSON schema describing this resource: `cloudar-codebuild-build.json`
- Resource handlers in `cloudar_codebuild_build/handlers.py`

> Don't modify `models.py` by hand, any modifications will be overwritten when the `generate` or `package` commands are run.

## Contract Tests
- To run the contract tests you need to have a CodeBuild Project that matches the name that's defined in `overrides.json`
- Running the contract tests will start builds in that project
