from typing import List, Optional

class PathwayNode:
    def __init__(
        self,
        id: str,
        name: Optional[str] = None,
        smiles: Optional[str] = None,
        depth: Optional[int] = None,
        atom_count: Optional[int] = None,
        idcomp: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.smiles = smiles
        self.depth = depth
        self.atom_count = atom_count
        self.idcomp = idcomp
    def to_dict(self):
        return self.__dict__


class PathwayLink:
    def __init__(
        self,
        id: str,
        idreaction: str,
        source: int,
        target: int,
        name: Optional[str] = None,
        multistep: Optional[bool] = False,
        ec_numbers: Optional[List[dict]] = None,
    ):
        self.id = id
        self.idreaction = idreaction
        self.source = source
        self.target = target
        self.name = name
        self.multistep = multistep
        self.ec_numbers = ec_numbers or []
    def to_dict(self):
        return self.__dict__


class Pathway:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        is_incremental: bool,
        is_predicted: bool,
        reviewed: Optional[bool] = False,
        nodes: Optional[List[PathwayNode]] = None,
        links: Optional[List[PathwayLink]] = None,
        pathway_name: Optional[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.is_incremental = is_incremental
        self.is_predicted = is_predicted
        self.reviewed = reviewed
        self.nodes = nodes or []
        self.links = links or []
        self.pathway_name = pathway_name
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_incremental": self.is_incremental,
            "is_predicted": self.is_predicted,
            "reviewed": self.reviewed,
            "nodes": [node.to_dict() for node in self.nodes],
            "links": [link.to_dict() for link in self.links],
            "pathway_name": self.pathway_name
        }

