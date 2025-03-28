# graph.py
import graphviz


def build_dungeon_graph(visited_rooms: list, all_rooms: list) -> graphviz.Digraph:
    """Строит граф с туннелями, без пересечений, с разветвлениями через промежуточные узлы"""
    graph = graphviz.Digraph()
    graph.attr(
        rankdir='TB',
        bgcolor='#000000',
        fontcolor='#FFFFFF',
        labelloc='t',
        fontname='Press Start 2P',
        margin='0',
        pad='0.5',
        nodesep='0.25',
        ranksep='1.2',
        splines='ortho'
    )

    all_rooms_dict = {room['id']: room for room in all_rooms}

    node_style = {
        'shape': 'box',
        'style': 'filled',
        'fillcolor': '#000000',
        'fontcolor': '#FFFFFF',
        'color': '#8B0000',
        'penwidth': '3',
        'fontsize': '12',
        'width': '0',
        'height': '0',
        'fixedsize': 'false',
        'margin': '0.4,0.3'
    }

    tunnel_style = {
        'color': '#FFFFFF',
        'penwidth': '8',
        'arrowhead': 'none',
        'dir': 'none',
        'weight': '2'
    }

    # Добавляем комнаты
    for room_id in visited_rooms:
        room = all_rooms_dict.get(room_id)
        if room:
            current_style = node_style.copy()
            if room['id'] == visited_rooms[-1]:
                current_style.update({
                    'color': '#FF0000',
                    'penwidth': '4'
                })

            name = room['name']
            if len(name) > 15:
                words = name.split()
                if len(words) > 1:
                    name = '\n'.join(words)
                else:
                    name = '\n'.join([name[i:i + 10] for i in range(0, len(name), 10)])

            graph.node(str(room['id']), label=name, **current_style)

    # Обрабатываем соединения через промежуточные узлы
    edge_id_counter = 0
    connections = set()

    for room_id in visited_rooms:
        room = all_rooms_dict.get(room_id)
        if room:
            exits = [exit_data['target_room'] for exit_data in room.get('exits', []) if exit_data['target_room'] in visited_rooms]

            if not exits:
                continue

            if len(exits) == 1:
                # Прямое соединение, если только один выход
                target = exits[0]
                pair = tuple(sorted((room_id, target)))
                if pair not in connections:
                    graph.edge(str(room_id), str(target), **tunnel_style)
                    connections.add(pair)
            else:
                # Промежуточный узел
                hub_id = f"hub_{room_id}_{edge_id_counter}"
                edge_id_counter += 1

                # Добавляем невидимый узел
                graph.node(hub_id, label="", shape="point", width="0.01", height="0.01", style="invis")

                # Соединяем комнату с промежуточным узлом (одна толстая линия)
                graph.edge(str(room_id), hub_id, **tunnel_style)

                for target in exits:
                    pair = tuple(sorted((room_id, target)))
                    if pair not in connections:
                        # Соединение от хаба к целевой комнате
                        graph.edge(hub_id, str(target), **tunnel_style)
                        connections.add(pair)

    return graph