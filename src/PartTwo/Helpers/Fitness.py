import random

import appSettings
import PartTwo.Helpers.DB as db


def get_all_stations(with_where):
    """
    Select all the stations from the database

    :return:
    String array of distinct station names
    """
    r = []
    conn_str = appSettings.get_conn_str()  # get the connection string
    query = "SELECT distinct (tpl) FROM nrch_livst_a51 where pta is not null or ptd is not null or arr_at is not null or dep_at is not null"  #set the query
    result = db.run_query(conn_str, query,True)  # run the query on the database
    for i in result:  # for all the station rows
        r.append(i.split(",")[0].replace(" ", "").replace("'", ""))  # format the string to get
    return r


def sim_result(data, targets):
    """
    Simulate a random result in the dataset

    :param data:
    all the datasets
    :param targets:
    all the matching targets

    :return:
    A random datapoint and matching target
    """
    index = random.randint(0,len(data) -1)  # random dataset
    data_point = data[index]  # set the datapoint
    target = targets[index]  # set the matching target result
    return data_point, target


def get_rid_data(max_count):
    """
    Get the top RIDs from the data

    :param max_count:
    Max number of RIDs to return
    :return:
    Array of RIDs from the database
    """
    conn_str = appSettings.get_conn_str()  # get the connection string
    query = 'SELECT distinct rid from nrch_livst_a51'  # set the query
    rids = db.run_query(conn_str, query,True)  #execute the query
    if len(rids) > max_count:  #if the array is longer than the
        rids = rids[:max_count]  # limit else it takes 4 hours just to load the data
    return rids
