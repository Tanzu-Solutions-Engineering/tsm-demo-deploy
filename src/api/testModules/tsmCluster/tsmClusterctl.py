from tsm import tsm
import os, time
import argparse
import sys


def main( action: str, cluster_name: str) -> int:

    try:

        tsm_api_server = os.environ['TSM_API_SERVER']
        tsm_api_key = os.environ['TSM_API_KEY']
    
        tsm_obj = tsm.TSM(tsm_api_server, tsm_api_key)

    except KeyError:
        print('ERROR - env variables TSM_API_SERVER and/or TSM_API_KEY missing')
        return
    
    if action == 'add': 
    
        try: 

            status = None
            old_status = None

            print('Adding cluster to TSM, please wait...', flush=True)
            tsm_obj.add_cluster(cluster_name)

            while True:

                details = tsm_obj.get_cluster_details(cluster_name)
                
                status = details['status']['state']

                if status != old_status:
                    
                    print('')
                    print(f'Adding cluster to TSM status: {status} ', end="", flush=True)
                    old_status = status

                    if status == 'Ready':
                        break
                else:
                    print('.', end="", flush=True)
                
                time.sleep(5)
                
            return(0)

        except tsm.ClusterExistsError as ce:
            print(ce)
            return(1)
        except Exception as e:
            print(e)
            return(1)

    elif action == 'remove':

        try: 

            status = None
            old_status = None

            print('Deleting cluster from TSM, please wait...', flush=True)
            tsm_obj.delete_cluster(cluster_name)
                
            return(0)

        except tsm.ClusterNotExistsError as cne:
            print(cne)
            return(1)
        except Exception as e:
            print(e)
            return(1)




if __name__ == 'addCluster' or __name__ == '__main__':
    #print(sys.argv[1])
    sys.exit(main(sys.argv[1], sys.argv[2]))