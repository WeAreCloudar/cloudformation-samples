# Cloudar::CodeBuild::Build

Start a CodeBuild Build. It's highly recommended to either write the CodeBuild logs to S3/CloudWatch, or to  have prevent this resource from being deleted when CloudFormation performs a rollback

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "Cloudar::CodeBuild::Build",
    "Properties" : {
        "<a href="#projectname" title="ProjectName">ProjectName</a>" : <i>String</i>,
        "<a href="#environmentvariablesoverride" title="EnvironmentVariablesOverride">EnvironmentVariablesOverride</a>" : <i>[ <a href="environmentvariable.md">EnvironmentVariable</a>, ... ]</i>,
    }
}
</pre>

### YAML

<pre>
Type: Cloudar::CodeBuild::Build
Properties:
    <a href="#projectname" title="ProjectName">ProjectName</a>: <i>String</i>
    <a href="#environmentvariablesoverride" title="EnvironmentVariablesOverride">EnvironmentVariablesOverride</a>: <i>
      - <a href="environmentvariable.md">EnvironmentVariable</a></i>
</pre>

## Properties

#### ProjectName

The name of the AWS CodeBuild build project to start running a build

_Required_: Yes

_Type_: String

_Pattern_: <code>^[a-zA-Z0-9_-]{2,}$</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### EnvironmentVariablesOverride

_Required_: No

_Type_: List of <a href="environmentvariable.md">EnvironmentVariable</a>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the BuildId.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### BuildId

The Identifier of the build

#### Arn

The Arn of the build

#### BuildNumber

The number of the build

