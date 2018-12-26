import sys
from Qt import QtWidgets, QtCore
import qdarkstyle
from nodegraph import GraphModel, GraphView


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    view = GraphView()
    model = GraphModel()
    view.set_model(model)

    # import pdb; pdb.set_trace()

    nodes = []
    for i in range(2):
        node = model.create_node(QtCore.QRectF(0, 0, 50, 50))
        node.create_plug('out', QtCore.QRectF(0, 0, 10, 10))
        node.create_socket('in', QtCore.QRectF(0, 0, 10, 10))
        nodes.append(node)


    model.connect(nodes[0].sockets['in'], nodes[1].plugs['out'])

    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
