from aws_cdk import (
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_codecommit as codecommit,
    aws_eks as eks,
    core
)
from . import fluxcd_cluster
class FluxcdConstruct(core.Construct):

    def __init__(
        self, 
        scope: core.Construct, 
        id: str, 
        eks_base_cluster: eks.Cluster,
        git_user,
        git_password        
    ) -> None:        
        
        super().__init__(scope=scope, id=id)
        
        name = scope.node.try_get_context("name")                
        region = scope.region  
            
        # Repo for Kubernetes infraestructure
        codecommit_repo_kubernetes = codecommit.Repository(
            scope=self, 
            id=f"{name}-kubernetes-git",
            repository_name=f"kubernetes-infra-{name}",
            description=f"Kubernetes Infra Code"
        )
        self.k8s_infra_git_host = "git-codecommit." + region + ".amazonaws.com/v1/repos/" + codecommit_repo_kubernetes.repository_name
        core.CfnOutput(
            scope=self,
            id="k8s_infrastructure_repository",
            value=codecommit_repo_kubernetes.repository_clone_url_http
        )
        fluxcd_cluster.FluxcdCluster(
            scope=self,
            eks_base_cluster=eks_base_cluster,
            git_user=git_user,
            git_password=git_password,
            git_repository=self.k8s_infra_git_host
        )

