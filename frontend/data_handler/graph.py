import graphviz


def build_dungeon_graph(visited_rooms: list, all_rooms: list) -> graphviz.Digraph:
    """Строит граф с угловатыми соединениями в пиксельном стиле"""
    graph = graphviz.Digraph()
    graph.attr(
        rankdir='TB',
        bgcolor='#000000',
        fontcolor='#FFFFFF',  # Белый текст
        labelloc='t',
        fontname='Press Start 2P',
        margin='0.5',
        pad='0.5',
        nodesep='0.8',
        ranksep='1.2',
        splines='ortho'  # Угловатые линии соединений
    )

    all_rooms_dict = {room['id']: room for room in all_rooms}

    # Стиль узлов
    node_style = {
        'shape': 'box',
        'style': 'filled',
        'fillcolor': '#000000',
        'fontcolor': '#FFFFFF',  # Белый текст
        'color': '#8B0000',
        'penwidth': '3',
        'fontsize': '10'
    }

    # Стиль рёбер
    edge_style = {
        'color': '#FFFFFF',  # Белые линии
        'penwidth': '2',
        'arrowhead': 'vee',  # Угловатая стрелка
        'arrows': '1.2'
    }

    for room_id in visited_rooms:
        room = all_rooms_dict.get(room_id)
        if room:
            current_node_style = node_style.copy()
            if room['id'] == visited_rooms[-1]:
                current_node_style['color'] = '#FF0000'  # Красная рамка для текущей комнаты

            graph.node(str(room['id']),
                       label=room['name'],
                       **current_node_style)

            for exit_data in room.get('exits', []):
                target_room = all_rooms_dict.get(exit_data['target_room'])
                if target_room:
                    graph.edge(str(room['id']),
                               str(target_room['id']),
                               **edge_style)

    return graph