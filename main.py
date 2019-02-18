import os
import json
import enaml
import pandas as pd
import tornado.web
import tornado.websocket
import tornado.ioloop
from web.core.app import WebApplication

with enaml.imports():
    from viewer import Viewer

log = tornado.web.app_log


SMD_COMPONENTS = pd.read_csv('smd-components.csv')


# Update man
MANUFACTURERS = {
    'Agi': 'Agilent (was HP)',
    'Fch': 'Fairchild',
    'HP': 'Hewlett-Packard (Now Agilent)',
    'Inf': 'Infineon',
    'ITT': 'ITT Semiconductors',
    'MC': 'Mini-Circuits',
    'Mot': 'Motorola (ON Semi)',
    'Nat': 'National Semiconductor',
    'Nec': 'NEC',
    'NJRC': 'New Japan Radio Co',
    'ON': 'ON Semiconductors',
    'Phi': 'Philips',
    'Roh': 'Rohm',
    'SGS': 'SGS-Thompson',
    'Sie': 'Siemens (now Infineon)',
    'Sil': 'Siliconix (Vishay-Silliconix)',
    'Tem': 'Temic Semiconductors',
    'Tfk': 'Telefunken (Vishay-Telefunken)',
    'Tok': 'Toko Inc.',
    'Zet': 'Zetex',
}

SMD_COMPONENTS.replace({'Manufacturer': MANUFACTURERS}, inplace=True)

# Holds the rendered view so a websocket can retrieve it later
CACHE = {}

class ViewerHandler(tornado.web.RequestHandler):

    def get(self):
        viewer = Viewer(
            request=self.request,
            response=self,
            dataframe=SMD_COMPONENTS,
        )

        # Store the viewer in the cache
        CACHE[viewer.ref] = viewer

        self.write(viewer.render())


class ViewerWebSocket(tornado.websocket.WebSocketHandler):
    viewer = None

    def open(self):
        # Store the viewer in the cache
        ref = self.get_argument("ref")
        if ref not in CACHE:
            log.error(f"Viewer with ref={ref} does not exist!")
            self.close()
            return

        # Get a viewer reference
        self.viewer = CACHE[ref]

        # Setup an observer to watch changes on the enaml view
        self.viewer.observe('modified', self.on_dom_modified)

    def on_message(self, message):
        """ When we get an event from js, lookup the node and invoke the
        action on the enaml node.

        """
        change = json.loads(message)
        log.debug(f'Update from js: {change}')

        # Lookup the node
        ref = change.get('ref')
        if not ref:
            return
        nodes = self.viewer.xpath('//*[@ref=$ref]', ref=ref)
        if not nodes:
            return  # Unknown node
        node = nodes[0]

        # Trigger the change on the enaml node
        if change.get('type') and change.get('name'):
            if change['type'] == 'event':
                trigger = getattr(node, change['name'])
                trigger()
            elif change['type'] == 'update':
                # Trigger the update
                setattr(node, change['name'], change['value'])
        else:
            log.warning(f"Unhandled event {self} {node}: {change}")

    def on_dom_modified(self, change):
        """ When an event from enaml occurs, send it out the websocket
        so the client's browser can update accordingly.

        """
        log.debug(f'Update from enaml: {change}')
        self.write_message(json.dumps(change['value']))

    def on_close(self):
        log.debug(f'WebSocket {self} closed')
        if self.viewer is not None:
            self.viewer.unobserve('modified', self.on_dom_modified)


def run():
    # Needed to create enaml components
    enaml_app = WebApplication()

    # Start the tornado app
    app = tornado.web.Application([
        (r'/', ViewerHandler),
        (r'/websocket/', ViewerWebSocket),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {
            'path': os.path.dirname(__file__)}),
    ])
    app.listen(int(os.environ.get('PORT', 5000)))
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    run()
