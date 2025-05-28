import json
from first_attemps.pathways_json.model_Pathways import Pathway , PathwayNode, PathwayLink

def load_pathways():
    with open("./envipathData/soil.json", "r", encoding="utf-8") as f:
        packages_data = json.load(f)
        raw_pathways = packages_data.get("pathways", [])
    return raw_pathways

def parse_pathways(raw_pathways):
    pathways = []
    for pathway in raw_pathways:
        nodes = []
        for node in pathway.get("nodes", []):
            nodes.append(PathwayNode(
                id=node["id"],
                name=node.get("name"),
                smiles=node.get("smiles"),
                depth=node.get("depth"),
                atom_count=node.get("atom_count"),
                idcomp=node.get("idcomp")
            ))

        links = []
        for link in pathway.get("links", []):
            links.append(PathwayLink(
                id=link["id"],
                idreaction=link["idreaction"],
                source=link["source"],
                target=link["target"],
                name=link.get("name"),
                multistep=link.get("multistep", False),
                ec_numbers=link.get("ec_numbers", []),
            ))
        pathway = Pathway(
            id=pathway["id"],
            name=pathway["name"],
            description=pathway.get("description", ""),
            is_incremental=pathway.get("isIncremental", "false") == "true",
            is_predicted=pathway.get("isPredicted", "false") == "true",
            nodes=nodes,
            links=links,
            pathway_name=pathway.get("pathwayName")
        )
        pathways.append(pathway)
    return pathways


def load_parse_package():
    pathway_objects = parse_pathways(load_pathways())
    return pathway_objects

def clean_pathway(pathways):
    cleaned = []
    for pathway in pathways:
        # We clean the nodes of false ones (usually reactions)
        cleaned_nodes = []
        index_map = {}
        for i, node in enumerate(pathway.nodes):
            if not node.smiles or "reaction" in (node.name or "").lower() or node.depth is None or node.depth <  0 :
                continue
            index_map[i] = len(cleaned_nodes)
            cleaned_nodes.append({
                "name": node.name,
                "smiles": node.smiles,
                "depth": node.depth,
            })

        # To keep the links with nodes still here, but might not work so not sure
        cleaned_links = []
        for link in pathway.links:
            if link.source in index_map and link.target in index_map:
                cleaned_links.append({
                    "name": link.name,
                    "source": index_map[link.source],
                    "target": index_map[link.target],
                    "multistep": link.multistep,
                })

        if not cleaned_nodes:
            continue
        cleaned_pathway = {
            "name": pathway.name,
            "description": pathway.description,
            "nodes": cleaned_nodes,
            "links": cleaned_links,
        }
        if pathway.pathway_name is not None and pathway.pathway_name != pathway.name:
            cleaned_pathway["pathway_name"] = pathway.pathway_name
        cleaned.append(cleaned_pathway)

    return cleaned

def save_pathways_to_json(pathways, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        if pathways and isinstance(pathways[0], dict):
            json.dump(pathways, f, indent=2)
        else:
            json.dump([p.to_dict() for p in pathways], f, indent=2)