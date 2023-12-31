#!/bin/env python3
# -- coding: utf-8 --
import os
import sys
import XenAPI
import json
import mysql.connector

# try:
ip = 0
lista = ['0.0.0.0', '0.0.0.0', '0.0.0.0', '0.0.0.0', '0.0.0.0', '0.0.0.0'] #local para os IP dos hosts
for ip in lista:
    session = XenAPI.Session(f'http://{ip}')
    session.login_with_password("user", "senha")

    # conexão com host hypervisor
    host = session.xenapi.host.get_all()[0]
    hypervisor_host = session.xenapi.host.get_hostname(host)
    sys.stdout.write(f" Host conectado do master do cluster {hypervisor_host} \n ")

    """
    #para saber a rede
    rede = session.xenapi.host.get_all()[0]
    network = session.xenapi.host.get_address(rede)
    sys.stdout.write(f"rede {network}")
    print(network)
     """

    # verificar as informações do pool de conexão esta conectado
    pool = session.xenapi.pool.get_all()[0]
    pool_record = session.xenapi.pool.get_record(pool)
    sys.stdout.write(f" Pool conectado com sucesso POOL: " + pool_record['name_label'] + '\n')
    # if pool_record["name_label"] != "OpaqueRef:NULL":
    #    print(pool_record)

    # pegando as informações das vms
    pool_vms = session.xenapi.VM.get_all()
    pool = session.xenapi.pool.get_all()[0]
    pool_uuid = session.xenapi.pool.get_uuid(pool)

    con = mysql.connector.connect(host='localhost', database='vmsxeserver', user='xen', password='123456')
    if con.is_connected():
        db_info = con.get_server_info()
        print("conectado ao servidor MySQL versão ", db_info)
        cursor = con.cursor()
        cursor.execute("select database();")
        linha = cursor.fetchone()
        print("conectado ao banco de dados", linha)

    for vm in pool_vms:
        vm_record = session.xenapi.VM.get_record(vm)

        # verificar se realmente é uma vm e não um dom 0 ou template ou snapshot
        if not (vm_record["is_control_domain"]) and not (vm_record["is_a_snapshot"]) and not (
                vm_record["is_a_template"]):
            data = {
                'short_message': os.path.basename(__file__).split('.')[0],
                '_pool_uuid': pool_uuid,
                '_name_description': vm_record["name_description"],
                '_name_label': vm_record["name_label"],
                '_power_state': vm_record["power_state"],
                '_vm_uuid': vm_record["uuid"],
                '_VCPUs_at_startup': vm_record["VCPUs_at_startup"],
                '_VCPUs_max': vm_record["VCPUs_max"],
                '_memory_dynamic_max': int(vm_record["memory_dynamic_max"]),
                '_memory_dynamic_min': int(vm_record["memory_dynamic_min"]),
                '_memory_static_max': int(vm_record["memory_static_max"]),
                '_dom_arch': vm_record["domarch"],
                '_tags': vm_record["tags"],

            }

            if vm_record["resident_on"] != "OpaqueRef:NULL":
                data['_host_uuid'] = session.xenapi.host.get_uuid(vm_record["resident_on"])
                data['_host_hostname'] = session.xenapi.host.get_hostname(vm_record["resident_on"])
                # data['_host_network'] = session.xenapi.network.get_all(vm_record["resident_on"])

            # gera lista em json
            dados = json.dumps(data, indent=4, sort_keys=True)
            print(dados)

            # teste de loop para pegar valores
            # for chave in data.keys():
            #    print(f'Campo= {chave} e Valor = {data[chave]}')

            # print(type(data))
            # print(data.get('_host_hostname'))
            # print(data.keys()) #pega as keys
            # print(data.values()) #pega os valores

# finally:
#    session.xenapi.session.logout()

