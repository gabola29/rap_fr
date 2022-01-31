# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 14:47:10 2021

@author: gabri
"""

import networkx as nx
import pandas as pd
import numpy as np
from statistics import mean


def calculation_individual_metrics(network):
    """
    Compute all the indidual metrics for network analysis.

    Parameters
    ----------
    network : nx.classes.graph.Graph
        The network you want to analyse.

    Returns
    -------
    tuple
        The tuple, containing dataframe for each metrics.

    """
    # on recupère toutes les metrics interessantes
    
    degree = dict(nx.degree(network))
    clustering = dict(nx.clustering(network))
    betweeness = dict(nx.betweenness_centrality(network))
    centrality = dict(nx.degree_centrality(network))
    triangles = dict(nx.triangles(network))
    eccentricity = dict(nx.eccentricity(network))
    close = dict(nx.closeness_centrality(network))
    page = dict(nx.pagerank(network))
    eig = dict(nx.eigenvector_centrality_numpy(network, max_iter=200))
    square = dict(nx.square_clustering(network))
    mouloud_achour = dict(nx.number_of_cliques(network))
    degree_average_voisin = dict(nx.average_neighbor_degree(network))
    
    # on fait des df pour chaque echantillon

    degree_df = pd.DataFrame.from_dict(degree, orient='index', columns=['degree'])
    clustering_df = pd.DataFrame.from_dict(clustering, orient='index', columns=['clustering'])
    betweeness_df = pd.DataFrame.from_dict(betweeness, orient='index', columns=['betweeness'])
    centrality_df = pd.DataFrame.from_dict(centrality, orient='index', columns=['centrality'])
    triangles_df = pd.DataFrame.from_dict(triangles, orient='index', columns=['triangles'])
    eccentricity_df = pd.DataFrame.from_dict(eccentricity, orient='index', columns=['eccentricity'])
    close_df = pd.DataFrame.from_dict(close, orient='index', columns=['closeness'])
    page_df = pd.DataFrame.from_dict(page, orient='index', columns=['page_rank'])
    eig_df = pd.DataFrame.from_dict(eig, orient='index', columns=['eigen_centrality'])
    square_df = pd.DataFrame.from_dict(square, orient='index', columns=['square_clustering'])
    clic_df = pd.DataFrame.from_dict(mouloud_achour, orient='index', columns=['clique'])
    degree_average_voisin_df = pd.DataFrame.from_dict(degree_average_voisin, orient='index',
                                                      columns=['degree_average_voisin'])
    
    # on fait un try except pour le truc de KATZ car parfois ça ne converge pas
    try:
        katz = dict(nx.katz_centrality(network, max_iter=2000))
        katz_df = pd.DataFrame.from_dict(katz, orient='index', columns=['katz'])
        
    except nx.PowerIterationFailedConvergence:
        
        print('Warning : convergence failed for katz metric')
        katz_df = pd.DataFrame({
            'index':list(network.nodes),
            'katz':len(list(network.nodes))*[np.NaN]
        }).set_index('index', drop=True)

    return tuple([degree_df, clustering_df, betweeness_df, centrality_df, triangles_df,
                  eccentricity_df, close_df, page_df, eig_df, square_df, clic_df,
                  degree_average_voisin_df, katz_df])


def network_measures_to_dataframe(network, include_node_value=True, 
                                  raise_node_value_error=False):
    """
    Functions that is tranforming all individual network metrics into a DataFrame.

    Parameters
    ----------
    network : nx.classes.graph.Graph
        The network you want to analyse
    include_node_value : bool, optional
        If you want to include the node value or not. The default is True.
    raise_node_value_error : bool, optional
        If you want to raise an error when there are missing node value. The default is False.

    Raises
    ------
    ValueError
        Raised if the parameter raise_node_value_error is equal to True and if
        there is at least a missing value in the network.
    TypeError
        Raised when the network object is not a nx.classes.graph.Graph.

    Returns
    -------
    df : pd.DataFrame
        The DataFrame with all the individual metrics.

    """
    # on check s'il s'agit du bon type 
    if isinstance(network, nx.classes.graph.Graph) is True:
        
        # on fait la condition pour récupérer les valeurs des noeuds:
        if include_node_value is True:
            # on charge avec la valeur des noeuds
            node_with_value = dict(network.nodes(data=True))
            # problème s'il n'y a pas de valeur pour un des noeuds ça ne va pas marcher pour merge
            no_data_count = 0
            for key in node_with_value:
                if node_with_value[key] == {}:
                    no_data_count += 1
                    break
            # on check s'il y a des fails dans la valeur des noeuds
            if no_data_count == 0:
                node_df = pd.DataFrame.from_dict(node_with_value, orient='index', columns=['value'])
                
                values = calculation_individual_metrics(network)
                # on merge les df
                df = pd.concat([node_df, values[0], values[1], values[2], values[3], 
                                values[4], values[5], values[6], values[7], values[8],
                                values[9], values[10], values[11], values[12]], axis=1)
                df.reset_index(drop=False, inplace=True)
                df.rename(columns={'index': 'node'}, inplace=True)
                
            else:
                if raise_node_value_error is False: 
                    print('error in node value, node value not included in final result')
                    
                    # on calcul les metrics
                    values = calculation_individual_metrics(network)
                    
                    # on merge les df
                    df = pd.concat([values[0], values[1], values[2], values[3], values[4],
                                    values[5], values[6], values[7], values[8], values[9],
                                    values[10], values[11], values[12]], axis=1)
                    df.reset_index(drop=False, inplace=True)
                    df.rename(columns={'index': 'node'}, inplace=True)
                
                else:
                    raise ValueError('Problem with node values, at least one of the node have no data')
            
        else:
            # on calcul les metrics
            values = calculation_individual_metrics(network)
            
            # on merge les df
            df = pd.concat([values[0], values[1], values[2], values[3], values[4],
                            values[5], values[6], values[7], values[8], values[9],
                            values[10], values[11], values[12]], axis=1)
            df.reset_index(drop=False, inplace=True)
            df.rename(columns={'index': 'node'}, inplace=True)
    
    else:
        error_message = str("Wrong network type !!, receive {}, instead of nx.classes.graph.Graph").format(
            str(type(network)))
        raise TypeError(error_message)
    
    return df    


def overall_calculations(network):
    """
    Compute all the overral metrics for the network.

    Parameters
    ----------
    network : nx.classes.graph.Graph
        The network you wan to analyse.

    Raises
    ------
    TypeError
        If network is not an nx.classes.graph.Graph object.

    Returns
    -------
    calculation_dict : dict
        The dict containing all the calculations.

    """
    # on check s'il s'agit du bon type 
    if isinstance(network, nx.classes.graph.Graph) is True:
        
        calculation_dict = {}
        
        # on rempli le dict avec toutes les infos
        calculation_dict['number_of_nodes'] = network.number_of_nodes()
        calculation_dict['number_of_edges'] = network.number_of_edges()
        calculation_dict['average_degree'] = calculation_dict['number_of_edges']/calculation_dict['number_of_nodes']
        calculation_dict['average_clustering'] = nx.average_clustering(network)
        calculation_dict['diameter'] = nx.diameter(network)
        calculation_dict['radius'] = nx.radius(network)
        calculation_dict['barycenter'] = nx.barycenter(network)
        calculation_dict['average_shortest_path'] = nx.average_shortest_path_length(network)
        calculation_dict['transitivity'] = nx.transitivity(network)
        calculation_dict['density'] = nx.density(network)
        
        if len(calculation_dict['barycenter']) > 1:
            print("Warning more than one barycenter, average distance to barycenter is only for the first")
        
        all_shortest_path_to_barycenter = []
        for node in network.nodes:
            a = nx.shortest_path_length(network, source=node, target=nx.barycenter(network)[0])
            all_shortest_path_to_barycenter.append(a)
        
        calculation_dict['average_distance_to_barycenter'] = mean(all_shortest_path_to_barycenter)
        
    else:
        error_message = str("Wrong network type !!, receive {}, instead of nx.classes.graph.Graph").format(
            str(type(network)))
        raise TypeError(error_message)
        
    return calculation_dict


def distance_to_barycenter_for_each_node(network):
    """
    Compute the disatnce to barycenter for each node.

    Parameters
    ----------
    network : nx.classes.graph.Graph
        The network you wan to analyse.

    Returns
    -------
    distance_to_barycenter : dict
        The dict containing the distance for each node.

    """
    # on calcule le barycentre
    barycenter = nx.barycenter(network)
    
    # on créer un dico que l'on va remplir
    distance_to_barycenter = {}
    
    # on itere dessus car il peut y en avoir plusieurs
    if len(barycenter) > 1:
        for node in network.nodes:
            distance_to_barycenter[node] = []
            for bary_node in barycenter:
                dist = nx.shortest_path_length(network, source=node, target=bary_node)
                distance_to_barycenter[node].append(dist)
    else:
        for node in network.nodes:
            distance_to_barycenter[node] = nx.shortest_path_length(network, source=node, target=barycenter[0])
                
    return distance_to_barycenter
