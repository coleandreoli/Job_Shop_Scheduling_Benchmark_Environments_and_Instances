PRINTS = False
OUTPUT = False
MODE = 2

import os
import scheduling_environment.simulationEnv as sim
from data_parsers.custom_instance_parser import parse
from plotting.drawer import plot_gantt_chart, draw_precedence_relations

from solution_methods.GA.src.initialization import initialize_run
from solution_methods.GA.run_GA import run_GA
from solution_methods.CP_SAT.run_cp_sat import run_CP_SAT
import numpy as np
import warnings

os.chdir("/home/cole/madrid/sites")
import frappe

frappe.connect("test", db_name="cole")
from scheduling_environment import job, operation, machine, jobShop


# class Workstations:
#     def __init__(self) -> None:
#         self._workstations = []
#         self._mapped_names = {}

#     def add_workstation(self, machine: dict):
#         for ma in machine.keys():
#             if ma not in self._workstations:
#                 self._workstations.append(ma)

#     @property
#     def workstations(self):
#         return self._workstations

#     @property
#     def mapped_names(self):
#         return self._mapped_names

#     def processing_times(self, machine):
#         # all other workstations are 0 except in machine
#         processing_time = {}
#         for i, wo in enumerate(self._workstations):
#             self._mapped_names[f"machine_{i+1}"] = wo
#             if wo not in machine:
#                 processing_time[f"machine_{i+1}"] = 1
#             else:
#                 processing_time[f"machine_{i+1}"] = int(machine[wo])
#         return processing_time

#     @property
#     def num_of_workstations(self):
#         return len(self._workstations)


number_jobs = 0
number_total_machines = 0
number_operations = 0
workstations = {}
cole = []

class FrappeJobShop:
    def __init__(self):
        """
        wo(op(machine(alternative machines)))

        """
        self.workstations = {}
        self.rworkstations = {}
        self.operations = {}

        self.n_jobs = 0
        self.n_operations = 0
        self.n_machines = 0

        self.results = None
        self.jobShopEnv = None

        self.processing_info = {
            "instance_name": "custom_problem_instance",
            "jobs": [],
            "sequence_dependent_setup_times" : {},
        }

    @staticmethod
    def get_wo_names():
        # list of work orders names
        return frappe.get_all("Work Order")

    def get_wo(self, wos):
        process_wo = lambda wo: frappe.get_doc("Work Order", wo["name"]).as_dict()[
            "operations"
        ]
        return list(map(process_wo, wos))

    def get_altertive_workstations(self, name_op):
        alternatives = []
        for i in frappe.get_doc("Operation", name_op).as_dict()[
            "alternative_workstations"
        ]:
            alternatives.append(i["workstation"])
        return alternatives

    def get_machines(self, wo):
        for ops in wo:
            for op in ops:
                if not op["workstation"] in self.workstations.values():
                    self.workstations[f'machine_{len(self.workstations)+1}'] = op["workstation"]
                # Edge case were alternative is not populated
                for wks in self.get_altertive_workstations(op["operation"]):
                    if not wks in self.workstations.values():
                        self.workstations[f'machine_{len(self.workstations)+1}'] = wks
        # Reversed workstations dict
        self.rworkstations = {v: k for k, v in self.workstations.items()}
        self.n_machines = len(self.rworkstations)
        self.processing_info["nr_machines"] = self.n_machines

    def parse_wo(self, wo):
        for ops in wo:
            # TODO: fix data
            if len(ops) == 0:
                continue

            job = {
                "job_id": self.n_jobs,
                "operations": [],
                   }
            
            self.n_jobs += 1
            predecessors = None
            for op in ops:
                if op["time_in_mins"]*60 != int(op["time_in_mins"]*60):
                    raise ValueError(f'Operation: {op["operation"]} contains < single precision decimal time type: {op["time_in_mins"]}')
                
                op_time = int(op["time_in_mins"] * 60)
                o = {
                    "operation_id": self.n_operations,
                    "processing_times": {},
                    "predecessor": None,
                    }

                self.n_operations += 1

            
                m = {}
                m[self.rworkstations[op["workstation"]]] = op_time

                for wks in self.get_altertive_workstations(op["operation"]):
                    #o.add_operation_option(self.rworkstations[wks], op_time)
                    m[self.rworkstations[wks]] = op_time
                if len(m) == 0:
                    raise ValueError("no assigned machines")

                o["processing_times"] = m

                if predecessors is not None:
                    o["predecessor"] = self.n_operations - 2
                predecessors = self.n_operations - 2

                job["operations"].append(o)

                self.processing_info["jobs"].append(job)

    def get_sequence_dependent_setup_times(self):
        self.processing_info["sequence_dependent_setup_times"] = {
            self.rworkstations[i] : np.zeros((1000, 1000), dtype=int).tolist()
                for i in self.rworkstations
                    }

    def solve(self):
        parameters = {
            "instance": {"problem_instance": "custom_problem_instance"},
            "solver": {"time_limit": 3600, "model": "fjsp"},
            "output": {"logbook": True},
        }
        jobShopEnv = parse(self.processing_info)
        self.results, self.jobShopEnv = run_CP_SAT(jobShopEnv, **parameters)
        #return results, jobShopEnv

    def plot(self):
        draw_precedence_relations(self.jobShopEnv)
        plt = plot_gantt_chart(self.jobShopEnv)
        plt.show()

    def sanity(self):
        self._jobshop = parse(self.processing_info)
        print(self._jobshop)
        print(len(self._jobshop.jobs))
        print(len(self._jobshop.operations))
        print(len(self._jobshop.machines))

        print("=================")
        print(self._jobshop.jobs)
        print("=================")
        print(self._jobshop.operations)
        print("=================")
        print(self._jobshop.machines)
        print("=================")

    def main(self, wo_names):
        # wos = self.get_wo_names()
        wos = self.get_wo(wo_names)
        self.get_machines(wos)
        self.parse_wo(wos)
        self.get_sequence_dependent_setup_times()

        ##print(self.processing_info)
        #self.sanity()
        self.solve()
        self.plot()


if __name__ == "__main__":
    wo_names = FrappeJobShop.get_wo_names()
    foo = FrappeJobShop()
    foo.main(wo_names)