import os
import scheduling_environment.simulationEnv as sim
from data_parsers.custom_instance_parser import parse
from plotting.drawer import plot_gantt_chart
from solution_methods.GA.src.initialization import initialize_run
from solution_methods.GA.run_GA import run_GA
from solution_methods.CP_SAT.run_cp_sat import run_CP_SAT
import numpy as np


os.chdir("/home/cole/madrid/sites")
import frappe
frappe.connect("test", db_name="cole")
from scheduling_environment import job, operation, machine, jobShop

#js = jobShop.JobShop()


# number_jobs = 0
# number_total_machines = 0
# number_operations = 0

# workstations = {}
# operations = {}

# cole = []

# for i, wos in enumerate(frappe.get_all("Work Order")):
#     wo = frappe.get_doc("Work Order", wos["name"]).as_dict()

#     # Jobs
#     jb = job.Job(i)
#     number_jobs += 1


#     operations = []
#     pred = 0
#     for j, ops in enumerate(wo["operations"]):
#         if PRINTS == True:
#             print(ops["operation"])
#             print(ops["time_in_mins"])
#             print(ops["workstation"])

#         if pred == 0:
#             _pred = None
#             pred += 1
#         else:
#             _pred = number_operations - 1

#         # Operations
#         operation = {
#             "operation_id": number_operations,
#             "processing_times": {},
#             "predecessor": _pred,
#         }

#         operations[ops["operation"]] = 1212
#         op = operation(jb, i, number_operations)
#         number_operations += 1

#         # Machines
#         machine_name = f'{ops["workstation"]}'
#         processing_time = {machine_name: ops["time_in_mins"]}


#         y.add_workstation(processing_time)
#         number_total_machines += 1
#         operation["processing_times"] = processing_time
#         # operation['processing_times'] = y.processing_times(processing_time)
#         operations.append(operation)

#     #job["operations"] = operations
#     js.add_job()

#     cole.append(job)
#     if i == 3:
#         break


class FrappeJobShop:
    def __init__(self):
        """
        all data > work orders (wos)
        work orders > operations

        wo(op(machine))

        """
        self.number_jobs = 0
        self.number_total_machines = 0
        self.number_operations = 0
        self.workstations = {}
        self.operations = {}
        self._jobshop = jobShop.JobShop()

        self.n_jobs = 0
        self.n_operations = 0
        self.n_machines = 0
    
    def get_jobs(self):
        # list of work orders
        return frappe.get_all("Work Order")

    def get_wo(self, wos):
            process_wo = lambda wo: frappe.get_doc("Work Order", wo["name"]).as_dict()["operations"]
            return list(map(process_wo, wos))
    

            #print(ops_results)


    def parse_wo(self, wo):
        if all(element is None for element in wo):
            return
        print(wo[0][0].keys())
        for ops in wo:
            print(ops)
            print(ops["operation"])
            print(ops["time_in_mins"])
            print(ops["workstation"])

    def get_machines(self):
        pass

    def main(self):        
        wos = self.get_jobs()
        wo = self.get_wo(wos)
        #self.parse_wo(wo)
        print(wo)

if __name__ == '__main__':
    foo = FrappeJobShop()
    foo.main()