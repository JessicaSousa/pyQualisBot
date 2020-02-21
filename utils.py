from pyQualis import Search


class SearchBot(Search):
    def __init__(self, event="quadriênio"):
        super().__init__()
        self.event = event
    
    def set_event(self, event="quadriênio"):
        self.event = event

    def by_area(self, area):
         return super().by_area(area, self.event)
