from aws_cdk import (    
    aws_eks as eks,
    core as cdk
)

class ClusterConstruct(cdk.Construct):
    def __init__(self,scope,id,cluster_name):
        super().__init__(scope,id)                
        self._cluster_name = cluster_name
        self._create_resource()
    
    def _create_resource(self):
        self.cluster = eks.Cluster(
            scope=self,
            id=self._cluster_name,
            version=eks.KubernetesVersion.V1_18
        )
