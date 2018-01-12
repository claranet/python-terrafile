# python-terrafile

Manages external Terraform modules, controlled by a `Terrafile`.

This is basically a Python version of the tool described at [http://bensnape.com/2016/01/14/terraform-design-patterns-the-terrafile/](http://bensnape.com/2016/01/14/terraform-design-patterns-the-terrafile/)

Additionally pterrafile supports modules from Terraform Registry as well as modules in local directories, identified by a relative path starting with either `./` or `../`.


```shell
# registry module
tf-aws-lambda:
  source: "claranet/lambda/aws"
  version: "v0.1.0"

# local module
tf-aws-test:
  source: "../../modules/tf-aws-test"
```

## Installation

```shell
pip install terrafile
```

## Usage

```shell
pterrafile [path]
```

If `path` is provided, it must be the path to a `Terrafile` file, or a directory containing one. If not provided, it looks for the file in the current working directory.
