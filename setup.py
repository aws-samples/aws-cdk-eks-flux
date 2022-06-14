import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="fluxcd",
    version="0.0.1",

    description="A sample CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "fluxcd"},
    packages=setuptools.find_packages(where="fluxcd"),

    install_requires=[
        "aws-cdk.core>=2.0.0",
        "aws-cdk.aws_iam>=2.0.0",
        "aws-cdk.aws_sqs>=2.0.0",
        "aws-cdk.aws_sns>=2.0.0",
        "aws-cdk.aws_sns_subscriptions>=2.0.0",
        "aws-cdk.aws_s3>=2.0.0",
        "aws-cdk.aws_codecommit>=2.0.0",
        "aws-cdk.aws_codepipeline>=2.0.0",
        "aws-cdk.aws_codebuild>=2.0.0",
        "aws-cdk.aws_codepipeline_actions>=2.0.0",
        "aws-cdk.aws_eks>=2.0.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
