variable "appId" {
  description = "Azure Kubernetes Service Cluster service principal"
}

variable "password" {
  description = "Azure Kubernetes Service Cluster password"
}

variable "region" {
  default     = "West US 2"
}

variable "cluster_name" {
  type = string
}

variable "num_nodes" {
  default = 2
}

variable "node_size" {
  default = "Standard_D4_v3"
}

variable "k8s_version" {
  default = "1.20.9"
}
