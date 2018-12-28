from Qt import QtWidgets, QtGui, QtCore


class GraphView(QtWidgets.QGraphicsView):
    def __init__(self, *args, **kwargs):
        super(GraphView, self).__init__(*args, **kwargs)
        self.setViewportUpdateMode(self.FullViewportUpdate)

    def set_model(self, model):
        self.setScene(model)


class NodeItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, node_id, *args, **kwargs):
        self.editable = kwargs.pop('editable', True)
        self.id = node_id
        self.plugs = {}
        self.sockets = {}
        self.style = kwargs.pop('style', {})
        defaults = {
            'header_size': 20
        }
        for key in defaults:
            if key not in self.style:
                self.style[key] = defaults[key]
        super(NodeItem, self).__init__(*args, **kwargs)
        if self.editable:
            self.setFlags(self.ItemIsMovable | self.ItemIsSelectable)

    @property
    def header_size(self):
        return self.style['header_size']

    def create_plug(self, name, *args, **kwargs):
        self.plugs[name] = self._add_port(name, *args, **kwargs)
        self._layout_ports()

    def create_socket(self, name, *args, **kwargs):
        self.sockets[name] = self._add_port(name, *args, **kwargs)
        self._layout_ports()

    def _add_port(self, name, *args, **kwargs):
        port_class = kwargs.pop('port_class', PortItem)
        kwargs['parent'] = self
        port = port_class(name, *args, **kwargs)
        return port

    def _layout_ports(self):
        """" Lay out sockets and plugs on edges of the node.
        """
        rect = self.rect()
        port_height = float(rect.height() - self.header_size)
        # layout sockets
        if self.sockets:
            socket_spacing = port_height / float(len(self.sockets) + 1)
            for i, socket in enumerate(self.sockets.values()):
                socket.setPos(QtCore.QPointF(rect.x(), self.header_size + ((i + 1) * socket_spacing)))

        if self.plugs:
            plug_spacing = port_height / float(len(self.plugs) + 1)
            for i, plug in enumerate(self.plugs.values()):
                plug.setPos(QtCore.QPointF(rect.x() + rect.width(), self.header_size + ((i + 1) * plug_spacing)))


class ConnectionItem(QtWidgets.QGraphicsItem):
    def __init__(self, socket, plug, *args, **kwargs):
        super(ConnectionItem, self).__init__(*args, **kwargs)
        self._plug_pos = QtCore.QPointF(0, 0)
        self._socket_pos = QtCore.QPointF(0, 0)
        self.path = QtGui.QPainterPath()
        self.socket = socket
        if self.socket:
            self.socket.add_connection(self)
            self.set_socket_pos(self.socket.pos())
        self.plug = plug
        if self.plug:
            self.plug.add_connection(self)
            self.set_plug_pos(self.plug.pos())

    def set_plug_pos(self, pos):
        if pos != self._plug_pos:
            self._plug_pos = pos
            self._rebuild_points()

    def set_socket_pos(self, pos):
        if pos != self._socket_pos:
            self._socket_pos = pos
            self._rebuild_points()

    def boundingRect(self):
        return self.path.boundingRect().adjusted(-10, -10, 10, 10)

    def setPath(self, path):
        if self.path != path:
            self.path = path
            self.prepareGeometryChange()

    def paint(self, painter, options, widget):
        painter.drawPath(self.path)

    def _rebuild_points(self):
        path = QtGui.QPainterPath(self._plug_pos)
        path.cubicTo(
            QtCore.QPointF(((self._plug_pos.x() * 2) + self._socket_pos.x()) / 3.0, self._plug_pos.y()),
            QtCore.QPointF(((self._socket_pos.x() * 2) + self._plug_pos.x()) / 3.0, self._socket_pos.y()),
            self._socket_pos
        )
        self.setPath(path)


class PortItem(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, name, *args, **kwargs):
        super(PortItem, self).__init__(*args, **kwargs)
        self.name = name
        self.connections = []

    @property
    def node(self):
        return self.parent()

    def centerPos(self):
        return self.mapToScene(self.boundingRect().center())

    def setPos(self, pos):
        # convert position to center
        rect = self.boundingRect()
        new_pos = pos - QtCore.QPointF(rect.width() / 2.0, rect.height() / 2.0)
        super(PortItem, self).setPos(new_pos)

    def add_connection(self, connection):
        self.connections.append(connection)

    def paint(self, *args, **kwargs):
        super(PortItem, self).paint(*args, **kwargs)
        # Ensure all connections have updated positions
        for connection in self.connections:
            if connection.plug is self:
                connection.set_plug_pos(self.centerPos())
            elif connection.socket is self:
                connection.set_socket_pos(self.centerPos())


class GraphModel(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(GraphModel, self).__init__()
        self._nodes = {}
        self._current_id = -1
        self._setup_background()

    def connect(self, socket, plug, *args, **kwargs):
        connection_class = kwargs.pop('connetion_class', ConnectionItem)
        connection = connection_class(socket, plug, *args, **kwargs)
        self.addItem(connection)
        return connection

    def create_node(self, *args, **kwargs):
        node_class = kwargs.get('node_class') or NodeItem
        node_id = self._get_node_id()
        node = node_class(node_id, *args, **kwargs)
        self.addItem(node)
        self._nodes[node_id] = node
        return node

    def _get_node_id(self):
        self._current_id += 1
        return self._current_id

    def _setup_background(self):
        self.background_image = QtGui.QImage(QtCore.QSize(100, 100), QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter(self.background_image)
        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        painter.drawRect(QtCore.QRect(0, 0, 100, 100))
        painter.end()
        brush = QtGui.QBrush(self.background_image)
        self.setBackgroundBrush(brush)

