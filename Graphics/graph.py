import base64
import mermaid as md
from mermaid.graph import Graph
from IPython.display import Image
import matplotlib.pyplot as plt

graph = Graph('Sequence-diagram',"""
stateDiagram-v2
    [*] --> Still
    Still --> [*]

    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
""")

graphbytes = graph.encode('utf8')
base64_bytes = base64.urlsafe_b64encode(graphbytes)
base64_string = base64_bytes.decode('ascii')
Image(url='https://mermaid.ink/img/' + base64_string)

plt.savefig
