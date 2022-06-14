#!/usr/bin/env python3
 
from aws_cdk import App, Stack, Environment
from dockerpipeline.docker_pipeline import DockerPipelineConstruct
from fluxcd.fluxcd_construct import FluxcdConstruct
from cluster.cluster_construct import ClusterConstruct
import os
git_auth_user = os.environ["GIT_AUTH_USER"]
git_auth_key = os.environ["GIT_AUTH_KEY"]

app = App()

name = app.node.try_get_context("name")
region = app.node.try_get_context("region")

aws_env = Environment(region=region)
stack = Stack(scope=app,id=f"{name}-stack",env=aws_env)

cluster_construct = ClusterConstruct(
    scope=stack,
    id=f"{name}-cluster",
    cluster_name=f"{name}-cluster"
)
fluxcd_docker_pipeline = DockerPipelineConstruct(
    scope=stack,
    id=f"{name}-docker-pipeline"
)
fluxcd_construct = FluxcdConstruct(
    scope=stack,
    id=f"{name}-fluxcd",
    git_user=git_auth_user,
    git_password=git_auth_key,
    eks_base_cluster=cluster_construct.cluster
)

app.synth()