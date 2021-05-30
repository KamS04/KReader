from kivy.properties import NumericProperty
from kivy.uix.scrollview import ScrollView


class ScrollViewNoStutter(ScrollView):
    child_height = NumericProperty(0)

    def add_widget(self, widget, index=0):
        super().add_widget(widget, index=index)
        widget.bind(size=self.child_size_changed)
    
    def remove_widget(self, widget):
        super().remove_widget(widget)
        widget.unbind(size=self.child_size_changed)
    
    def child_size_changed(self, child, new_child_size):
        if new_child_size[1] > self.size[1]:
            # re-calculate scroll y
            # calculate distance between scrollview top and child top (in pixels)
            y_dist = (1.0 - self.scroll_y) * (self.child_height - self.height)
            # calculate new scroll_y that reproduces the above distance
            self.scroll_y = 1.0 - y_dist / (new_child_size[1] - self.height)
        
        self.child_height = new_child_size[1]

