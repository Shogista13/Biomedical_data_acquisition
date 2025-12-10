import math
import statistics

def process_spatial_parameters_in_single_frame(player_x,player_y,other_objects_x,other_objects_y):
    number_of_objects = len(other_objects_x)
    distances = [math.sqrt((player_x-other_objects_x[i])**2+(player_y-other_objects_y[i])**2) for i in range(number_of_objects)]
    if distances:
        collapsed = statistics.harmonic_mean(distances)
        #bierzemy średnią harmoniczną, bo bardzo na nią wpływają małe wartości (blisko coś),
        #dalsze obiekty mniej
    else:
        collapsed = 999999
        #nie wiemy co z tym zrobić, żeby nie psuło analizy,
        #pewnie damy po prostu jakąś dużą liczbę do środka, ale chyba sie nie zdarzy i tak
    return number_of_objects,collapsed

def process_spatial_parameters(player_x_list,player_y_list,other_objects_x_list,other_objects_y_list):
    numbers_of_objects = []
    collapsed_distances = []
    for frame in range(len(player_x_list)):
        number_of_objects,collapsed = process_spatial_parameters_in_single_frame(player_x_list[frame],player_y_list[frame],other_objects_x_list[frame],other_objects_y_list[frame])
        numbers_of_objects.append(number_of_objects)
        collapsed_distances.append(collapsed)
        #bierzemy liczbę przeciwników/pocisków i średnią harmoniczną odległości
    return numbers_of_objects,collapsed_distances
