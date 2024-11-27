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


class FrappeJobShop:
    def __init__(self):
        """
        wo(op(machine(alternative machines)))

        """
        self.workstations = {}
        self.rworkstations = {}
        self.operations = {}
        self._jobshop = jobShop.JobShop()

        self.n_jobs = 0
        # self.n_operations = 0
        # self.n_machines = 0

        self.results = None
        self.jobShopEnv = None

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
                    self.workstations[len(self.workstations)] = op["workstation"]
                # Edge case were alternative is not populated
                for wks in self.get_altertive_workstations(op["operation"]):
                    if not wks in self.workstations.values():
                        self.workstations[len(self.workstations)] = wks
        self.rworkstations = {v: k for k, v in self.workstations.items()}

    def set_machines(self):
        self._jobshop.set_nr_of_machines(len(self.workstations))
        for i in range(len(self.workstations)):
            self._jobshop.add_machine(machine.Machine(i))

    def parse_wo(self, wo):
        for ops in wo:
            # TODO: fix data
            if len(ops) == 0:
                continue
            j = job.Job(self.n_jobs)
            self.n_jobs += 1

            for op in ops:
                # if int(op["time_in_mins"]) == 0:
                #     raise ValueError("Duration is 0")

                # TODO: fix data
                if int(op["time_in_mins"]) == 0:
                    x = 5
                else:
                    x = int(op["time_in_mins"])

                o = operation.Operation(j, j.job_id, self._jobshop.nr_of_operations)
                self.operations[len(self.operations)] = op["operation"]
                # TODO: get alteratives
                o.add_operation_option(self.rworkstations[op["workstation"]], x)
                for wks in self.get_altertive_workstations(op["operation"]):
                    o.add_operation_option(self.rworkstations[wks], x)

                # o.add_operation_option(self.rworkstations[op["workstation"]], x)

                j.add_operation(o)
                self._jobshop.add_operation(o)

            self._jobshop.add_job(j)
        self._jobshop.set_nr_of_jobs(self.n_jobs)

    def solve(self):
        parameters = {
            "instance": {"problem_instance": "custom_problem_instance"},
            "solver": {"time_limit": 3600, "model": "fjsp"},
            "output": {"logbook": True},
        }

        results, jobShopEnv = run_CP_SAT(self._jobshop, **parameters)
        self.results = results
        self.jobShopEnv = jobShopEnv
        return results, jobShopEnv

    def plot(self):
        plt = plot_gantt_chart(self.jobShopEnv)
        plt.show()

    def sanity(self):
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
        self.set_machines()

        self.parse_wo(wos)
        # self.sanity()
        self.solve()
        self.plot()


if __name__ == "__main__":
    foo = FrappeJobShop()
    foo.main(FrappeJobShop.get_wo_names())
