from crawlers import Truyentranhtam

crawlers = [
    Truyentranhtam(),
]

for c in crawlers:
    c.start()