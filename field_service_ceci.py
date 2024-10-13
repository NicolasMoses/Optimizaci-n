import sys
import cplex
import os

TOLERANCE = 1e-6

class Orden:
    def __init__(self):
        self.id = 0
        self.beneficio = 0
        self.trabajadores_necesarios = 0
    
    def load(self, row):
        self.id = int(row[0])
        self.beneficio = int(row[1])
        self.trabajadores_necesarios = int(row[2])
        
class FieldWorkAssignment:
    def __init__(self):
        self.cantidad_dias = 6
        self.cantidad_turnos = 5
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []
        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []
        self.M = 50
    
    def load(self, filename):
        # Abrimos el archivo.
        with open(filename, 'r') as f:
            # Leemos la cantidad de trabajadores
            self.cantidad_trabajadores = int(f.readline())
            
            # Leemos la cantidad de órdenes
            self.cantidad_ordenes = int(f.readline())
            
            # Leemos cada una de las órdenes.
            self.ordenes = []
            for i in range(self.cantidad_ordenes):
                row = f.readline().strip().split(' ')
                orden = Orden()
                orden.load(row)
                self.ordenes.append(orden)
            
            # Leemos la cantidad de conflictos entre los trabajadores
            cantidad_conflictos_trabajadores = int(f.readline())
            
            # Leemos los conflictos entre los trabajadores
            self.conflictos_trabajadores = []
            for i in range(cantidad_conflictos_trabajadores):
                row = f.readline().strip().split(' ')
                self.conflictos_trabajadores.append(list(map(int, row)))
                
            # Leemos la cantidad de órdenes correlativas
            cantidad_ordenes_correlativas = int(f.readline())
            
            # Leemos las órdenes correlativas
            self.ordenes_correlativas = []
            for i in range(cantidad_ordenes_correlativas):
                row = f.readline().strip().split(' ')
                self.ordenes_correlativas.append(list(map(int, row)))
                
            # Leemos la cantidad de órdenes conflictivas
            cantidad_ordenes_conflictivas = int(f.readline())
            
            # Leemos las órdenes conflictivas
            self.ordenes_conflictivas = []
            for i in range(cantidad_ordenes_conflictivas):
                row = f.readline().strip().split(' ')
                self.ordenes_conflictivas.append(list(map(int, row)))

            # Leemos la cantidad de órdenes repetitivas
            cantidad_ordenes_repetitivas = int(f.readline())
            
            # Leemos las órdenes repetitivas
            self.ordenes_repetitivas = []
            for i in range(cantidad_ordenes_repetitivas):
                row = f.readline().strip().split(' ')
                self.ordenes_repetitivas.append(list(map(int, row)))

def get_instance_data():
    file_location = sys.argv[1].strip()
    instance = FieldWorkAssignment()
    instance.load(file_location)
    
    # Depuración
    print(f"Cantidad de trabajadores: {instance.cantidad_trabajadores}")
    print(f"Cantidad de órdenes: {instance.cantidad_ordenes}")
    for orden in instance.ordenes[:5]:  # Imprimir las primeras 5 órdenes
        print(f"Orden ID: {orden.id}, Beneficio: {orden.beneficio}, Trabajadores necesarios: {orden.trabajadores_necesarios}")
    return instance

def populate_by_row(my_problem, data):
    # Definimos y agregamos las variables del problema
    var_names = []
    obj = []
    lb = []
    ub = []
    types = []

    # Diccionarios para mapear variables
    x_vars = {}
    y_vars = {}
    z_vars = {}
    dia_trabajado_vars = {}
    ordenes_totales_vars = {}
    remuneracion_vars = {}
    s_vars = {}
    rem_tramo_vars = {}
    max_orden_var = 'max_orden'
    min_orden_var = 'min_orden'

    # Variables x_{o,d,t}
    for o in range(data.cantidad_ordenes):
        for d in range(data.cantidad_dias):
            for t in range(data.cantidad_turnos):
                var_name = f"x_{o}_{d}_{t}"
                var_names.append(var_name)
                obj.append(0.0)
                lb.append(0.0)
                ub.append(1.0)
                types.append('B')
                x_vars[(o, d, t)] = var_name

    # Variables y_{w,o,d,t}
    for w in range(data.cantidad_trabajadores):
        for o in range(data.cantidad_ordenes):
            for d in range(data.cantidad_dias):
                for t in range(data.cantidad_turnos):
                    var_name = f"y_{w}_{o}_{d}_{t}"
                    var_names.append(var_name)
                    obj.append(0.0)
                    lb.append(0.0)
                    ub.append(1.0)
                    types.append('B')
                    y_vars[(w, o, d, t)] = var_name

    # Variables z_o
    for o in range(data.cantidad_ordenes):
        var_name = f"z_{o}"
        var_names.append(var_name)
        obj.append(data.ordenes[o].beneficio)
        lb.append(0.0)
        ub.append(1.0)
        types.append('B')
        z_vars[o] = var_name

    # Variables dia_trabajado_{w,d}
    for w in range(data.cantidad_trabajadores):
        for d in range(data.cantidad_dias):
            var_name = f"dia_trabajado_{w}_{d}"
            var_names.append(var_name)
            obj.append(0.0)
            lb.append(0.0)
            ub.append(1.0)
            types.append('B')
            dia_trabajado_vars[(w, d)] = var_name

    # Variables ordenes_totales_w
    for w in range(data.cantidad_trabajadores):
        var_name = f"ordenes_totales_{w}"
        var_names.append(var_name)
        obj.append(0.0)
        lb.append(0.0)
        ub.append(data.M)
        types.append('I')
        ordenes_totales_vars[w] = var_name

    # Variables remuneracion_w
    for w in range(data.cantidad_trabajadores):
        var_name = f"remuneracion_{w}"
        var_names.append(var_name)
        obj.append(-1.0)  # Coeficiente negativo para restar la remuneración
        lb.append(0.0)
        ub.append(cplex.infinity)
        types.append('C')  
        remuneracion_vars[w] = var_name

    # Variables s_{w,i}
    for w in range(data.cantidad_trabajadores):
        for i in range(1, 5):
            var_name = f"s_{w}_{i}"
            var_names.append(var_name)
            obj.append(0.0)
            lb.append(0.0)
            ub.append(1.0)
            types.append('B')
            s_vars[(w, i)] = var_name

    # Variables rem_tramo_{w,i}
    for w in range(data.cantidad_trabajadores):
        for i in range(1, 5):
            var_name = f"rem_tramo_{w}_{i}"
            var_names.append(var_name)
            obj.append(0.0)
            lb.append(0.0)
            ub.append(cplex.infinity)
            types.append('C')
            rem_tramo_vars[(w, i)] = var_name

    # Variable max_orden
    var_names.append(max_orden_var)
    obj.append(0.0)
    lb.append(0.0)
    ub.append(data.M)
    types.append('I')

    # Variable min_orden
    var_names.append(min_orden_var)
    obj.append(0.0)
    lb.append(0.0)
    ub.append(data.M)
    types.append('I')

    # Añadimos todas las variables al modelo
    my_problem.variables.add(obj=obj, lb=lb, ub=ub, types=types, names=var_names)

    # Establecemos la dirección del problema
    my_problem.objective.set_sense(my_problem.objective.sense.maximize)

    # Definimos las restricciones del modelo
    add_constraint_matrix(
        my_problem,
        data,
        x_vars,
        y_vars,
        z_vars,
        dia_trabajado_vars,
        ordenes_totales_vars,
        remuneracion_vars,
        s_vars,
        rem_tramo_vars,
        max_orden_var,
        min_orden_var
    )

    # Exportamos el LP cargado en myprob con formato .lp
    input_path = sys.argv[1]
    output_path = input_path.replace('../data/', '../solutions/') + '_balanced_assignment_new.lp'
    my_problem.write(output_path)
    return x_vars, z_vars

def add_constraint_matrix(my_problem, data, x_vars, y_vars, z_vars, dia_trabajado_vars, 
ordenes_totales_vars, remuneracion_vars, s_vars, rem_tramo_vars, max_orden_var, min_orden_var):

    # Activación de z_o
    for o in range(data.cantidad_ordenes):
        indices = []
        values = []
        for d in range(data.cantidad_dias):
            for t in range(data.cantidad_turnos):
                indices.append(x_vars[(o, d, t)])
                values.append(1.0)
        indices.append(z_vars[o])
        values.append(-1.0)
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["E"],
            rhs=[0.0],
            names=[f"Activacion_z_{o}"]
        )

    # 1. Asignación Única de Órdenes
    for o in range(data.cantidad_ordenes):
        indices = []
        values = []
        for d in range(data.cantidad_dias):
            for t in range(data.cantidad_turnos):
                indices.append(x_vars[(o, d, t)])
                values.append(1.0)
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["L"], 
            rhs=[1.0], 
            names=[f"Asignacion_orden_{o}_{d}_{t}"]
        )

    # 2. Disponibilidad de trabajadores por turno
    for w in range(data.cantidad_trabajadores):
        for d in range(data.cantidad_dias):
            for t in range(data.cantidad_turnos):
                indices = []
                values = []
                for o in range(data.cantidad_ordenes):
                    indices.append(y_vars[(w, o, d, t)])
                    values.append(1.0)
                my_problem.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind=indices, val=values)],
                    senses=["L"],
                    rhs=[1.0]
                )

    # 3. Límite de días trabajados: Ningún trabajador trabaja los 6 dias.
    for w in range(data.cantidad_trabajadores):
        # a) sum_d dia_trabajado_{w,d} <=5
        indices = []
        values = []
        for d in range(data.cantidad_dias):
            indices.append(dia_trabajado_vars[(w, d)])
            values.append(1.0)
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["L"],
            rhs=[5.0], 
            names=[f"Trabajador_{w}_dias_a"]
        )

        # b) sum_{t,o} y[w,o,d,t] >= dia_trabajado_{w,d} para todo w,d
        for d in range(data.cantidad_dias):
            indices = []
            values = []
            for t in range(data.cantidad_turnos):
                for o in range(data.cantidad_ordenes):
                    indices.append(y_vars[(w, o, d, t)])
                    values.append(1.0)
            indices.append(dia_trabajado_vars[(w, d)])
            values.append(-1.0)
            my_problem.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=indices, val=values)],
                senses=["G"],
                rhs=[0.0], 
                names=[f"Trabajador_{w}_dias_b"]
            )

        # c) sum_{t,o} y[w,o,d,t] <= M * dia_trabajado_{w,d} para todo w,d
        for d in range(data.cantidad_dias):
            indices = []
            values = []
            for t in range(data.cantidad_turnos):
                for o in range(data.cantidad_ordenes):
                    indices.append(y_vars[(w, o, d, t)])
                    values.append(1.0)
            indices.append(dia_trabajado_vars[(w, d)])
            values.append(-data.M)
            my_problem.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=indices, val=values)],
                senses=["L"],
                rhs=[0.0], 
                names=[f"Trabajador_{w}_dias_c"]
            )

    # 4. Límite de turnos por dia: Ningún trabajador puede trabajar los 5 turnos de un dia.
    for w in range(data.cantidad_trabajadores):
        for d in range(data.cantidad_dias):
            indices = []
            values = []
            for t in range(data.cantidad_turnos):
                for o in range(data.cantidad_ordenes):
                    indices.append(y_vars[(w, o, d, t)])
                    values.append(1.0)
            my_problem.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=indices, val=values)],
                senses=["L"],
                rhs=[4.0], 
                names=[f"Trabajador_{w}_turnos"]
            )

    # 5. Órdenes conflictivas en un mismo trabajador: Hay pares de órdenes de trabajo
    # que no pueden ser satisfechas en turnos consecutivos de un trabajador.
    for conflict in data.ordenes_conflictivas:
        o1 = conflict[0]
        o2 = conflict[1]
        for w in range(data.cantidad_trabajadores):
            for d in range(data.cantidad_dias):
                for t in range(data.cantidad_turnos - 1):
                    indices = [y_vars[(w, o1, d, t)], y_vars[(w, o2, d, t + 1)]]
                    values = [1.0, 1.0]
                    my_problem.linear_constraints.add(
                        lin_expr=[cplex.SparsePair(ind=indices, val=values)],
                        senses=["L"],
                        rhs=[1.0]
                    )

    # 6. Asignación de Trabajadores a Órdenes: La suma de trabajadores asignados
    # a una orden debe ser igual al número de trabajadores necesarios si la orden está asignada.
    for o in range(data.cantidad_ordenes):
        for d in range(data.cantidad_dias):
            for t in range(data.cantidad_turnos):
                indices = []
                values = []
                for w in range(data.cantidad_trabajadores):
                    indices.append(y_vars[(w, o, d, t)])
                    values.append(1.0)
                indices.append(x_vars[(o, d, t)])
                values.append(-data.ordenes[o].trabajadores_necesarios)
                my_problem.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind=indices, val=values)],
                    senses=["E"],
                    rhs=[0.0],
                    names=[f"Asignacion_trabajadores_{o}_{d}_{t}"]
                )

    # 7. Órdenes Correlativas: Un par ordenado de órdenes correlativas A y B,
    # nos indica que si se satisface A, entonces debe satisfacerse B ese mismo día en el turno consecutivo.
    for corr in data.ordenes_correlativas:
        A = corr[0]
        B = corr[1]
        for d in range(data.cantidad_dias):
            for t in range(data.cantidad_turnos -1):
                indices = [x_vars[(A, d, t)], x_vars[(B, d, t +1)]]
                values = [1.0, -1.0]
                my_problem.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind=indices, val=values)],
                    senses=["L"],
                    rhs=[0.0]
                )

    # 8. Diferencia entre la cantidad de órdenes asignadas a cada trabajador:
    # La diferencia entre el trabajador con más órdenes asignadas y el trabajador
    # con menos órdenes no puede ser mayor a 10.

    # a) Cálculo de Órdenes Totales por Trabajador
    for w in range(data.cantidad_trabajadores):
        indices = [ordenes_totales_vars[w]]
        values = [-1.0]
        for d in range(data.cantidad_dias):
            for t in range(data.cantidad_turnos):
                for o in range(data.cantidad_ordenes):
                    indices.append(y_vars[(w, o, d, t)])
                    values.append(1.0)
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["E"],
            rhs=[0.0]
        )

    # b) max_orden - min_orden <=10
    indices = [max_orden_var, min_orden_var]
    values = [1.0, -1.0]
    my_problem.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=indices, val=values)],
        senses=["L"],
        rhs=[10.0]
    )
    # c) max_orden >= ordenes_totales_w para todo w
    for w in range(data.cantidad_trabajadores):
        indices = [max_orden_var, ordenes_totales_vars[w]]
        values = [1.0, -1.0]
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["G"],
            rhs=[0.0]
        )

    # d) min_orden <= ordenes_totales_w para todo w
    for w in range(data.cantidad_trabajadores):
        indices = [min_orden_var, ordenes_totales_vars[w]]
        values = [1.0, -1.0]
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["L"],
            rhs=[0.0]
        )

    # 9. Conflictos entre los trabajadores: Existen pares de trabajadores
    # que no pueden ser asignados a la misma orden.
    for conflict in data.conflictos_trabajadores:
        w1 = conflict[0]
        w2 = conflict[1]
        for o in range(data.cantidad_ordenes):
            for d in range(data.cantidad_dias):
                for t in range(data.cantidad_turnos):
                    indices = [y_vars[(w1, o, d, t)], y_vars[(w2, o, d, t)]]
                    values = [1.0, 1.0]
                    my_problem.linear_constraints.add(
                        lin_expr=[cplex.SparsePair(ind=indices, val=values)],
                        senses=["L"],
                        rhs=[1.0]
                    )

    # 10. Órden repetitiva para trabajador: Se pretende que un trabajador
    # no realice siempre el mismo tipo de órden.
    for conflict in data.ordenes_repetitivas:
        o1 = conflict[0]
        o2 = conflict[1]
        for w in range(data.cantidad_trabajadores):
            indices = []
            values = []
            for d in range(data.cantidad_dias):
                for t in range(data.cantidad_turnos):
                    indices.append(y_vars[(w, o1, d, t)])
                    values.append(1.0)
                    indices.append(y_vars[(w, o2, d, t)])
                    values.append(1.0)
            my_problem.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=indices, val=values)],
                senses=["L"],
                rhs=[1.0]
            )

    # 11. Cálculo de la Remuneración: Determinación del tramo de remuneración
    for w in range(data.cantidad_trabajadores):
        # a) s_{w,1} + s_{w,2} + s_{w,3} + s_{w,4} = 1
        indices = [s_vars[(w,1)], s_vars[(w,2)], s_vars[(w,3)], s_vars[(w,4)]]
        values = [1.0, 1.0, 1.0, 1.0]
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["E"],
            rhs=[1.0]
        )

        # b) Tramo 1 (0 a 5 órdenes): ordenes_totales_w <= 5 + M*(1 - s_{w,1})
        indices = [ordenes_totales_vars[w], s_vars[(w,1)]]
        values = [1.0, data.M]
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["L"],
            rhs=[5 + data.M]
        )

        # c) Tramo 2 (6 a 10 órdenes): ordenes_totales_w >= 6 - M*(1 - s_{w,2})
        indices = [ordenes_totales_vars[w], s_vars[(w,2)]]
        values = [1.0, -data.M]
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["G"],
            rhs=[6 - data.M]
        )
        ## ordenes_totales_w <= 10 + M*(1 - s_{w,2})
        indices = [ordenes_totales_vars[w], s_vars[(w,2)]]
        values = [1.0, data.M]
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["L"],
            rhs=[10 + data.M]
        )

        # d) Tramo 3 (11 a 15 órdenes): ordenes_totales_w >= 11 - M*(1 - s_{w,3})
        indices = [ordenes_totales_vars[w], s_vars[(w,3)]]
        values = [1.0, -data.M]
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["G"],
            rhs=[11 - data.M]
        )
        ## ordenes_totales_w <= 15 + M*(1 - s_{w,3})
        indices = [ordenes_totales_vars[w], s_vars[(w,3)]]
        values = [1.0, data.M]
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["L"],
            rhs=[15 + data.M]
        )

        # e) Tramo 4 (más de 15 órdenes): ordenes_totales_w >= 16 - M*(1 - s_{w,4})
        indices = [ordenes_totales_vars[w], s_vars[(w,4)]]
        values = [1.0, -data.M]
        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["G"],
            rhs=[16 - data.M]
        )

    # 12. Remuneración por trabajador
    for w in range(data.cantidad_trabajadores): # Iteramos por cada trabajador y por cada escalon de pago
        for i in range(1, 5):
        # Agregamos 2 restricciones para igualar la variable rem_tramo_vars[w, i]
        # a ordenes_totales_vars[w] cuando s_vars[w, i] está activo
             my_problem.linear_constraints.add(
                 lin_expr=[cplex.SparsePair(ind=[rem_tramo_vars[(w, i)], s_vars[(w, i)], ordenes_totales_vars[w]],
                                            val=[1.0, -data.M, -1.0])],
                 senses=["G"],
                 rhs=[-data.M],
                 names=[f"activacion_min_w{w}_i{i}"]
             )
             my_problem.linear_constraints.add(
                 lin_expr=[cplex.SparsePair(ind=[rem_tramo_vars[(w, i)], s_vars[(w, i)], ordenes_totales_vars[w]],
                                            val=[1.0, data.M, -1.0])],
                 senses=["L"],
                 rhs=[data.M],
                 names=[f"activacion_max_w{w}_i{i}"]
             )

    for w in range(data.cantidad_trabajadores):
        indices = [remuneracion_vars[w]]
        values = [1.0]
        for i in range(1, 5):
            coeficiente = 1000 if i == 1 else 1200 if i == 2 else 1400 if i == 3 else 1500
            indices.append(rem_tramo_vars[(w, i)])
            values.append(-coeficiente)

        my_problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=values)],
            senses=["E"],
            rhs=[0.0],
            names=[f"Remuneracion_w{w}"]
        )

def solve_lp(my_problem, data, z_vars, x_vars):
    # Resolvemos el ILP.
    my_problem.solve()

    # Obtenemos información de la solución
    status = my_problem.solution.get_status()
    status_string = my_problem.solution.get_status_string(status_code=status)
    print('Status solución: ', status_string, f'({status})')

    if status == my_problem.solution.status.MIP_optimal:
        objective_value = my_problem.solution.get_objective_value()
        print('Función objetivo: ', objective_value)

        # Obtenemos los valores de las variables
        variable_names = my_problem.variables.get_names()
        variable_values = my_problem.solution.get_values()

        # Crear el directorio si no existe
        os.makedirs('data/solutions', exist_ok=True)

        # Abrimos el archivo en la carpeta especificada
        with open('data/solutions/variables_output.txt', 'w') as file:
            # Guardamos las variables usadas
            for var_name, var_value in zip(variable_names, variable_values):
                file.write(f'{var_name}: {var_value}\n')

        # Imprimimos las variables usadas
        for var_name, var_value in zip(variable_names, variable_values):
            if var_value > TOLERANCE:
                print(f'{var_name}: {var_value}')
    elif status == my_problem.solution.status.MIP_infeasible:
        print('No se encontró una solución factible.')
    else:
        print('No se encontró una solución óptima.')


def main():
    # Obtenemos los datos de la instancia
    data = get_instance_data()

    # Definimos el problema de cplex
    prob_lp = cplex.Cplex()

    # Armamos el modelo
    x_vars, z_vars = populate_by_row(prob_lp, data)

    # Resolvemos el modelo
    solve_lp(prob_lp, data, z_vars, x_vars)

if __name__ == '__main__':
    main()
