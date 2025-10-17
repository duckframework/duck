"""
File Input components module (including FileDragAndDrop component).
"""
from duck.html.components.input import Input
from duck.html.components.script import Script
from duck.html.components.card import Card
from duck.html.components.label import Label


class FileInput(Input):
    """
    Basic FileInput component.
    """
    def on_create(self):
        super().on_create()
        self.props["type"] = "file"


class FileDragAndDrop(Card):
    """
    File Drag N Drop component with capabilities of dropping files rather than selecting only.
    
    Args:
        label_text (str): Text for the file drag n drop component
        input (FileInput): FileInput component with properties like `name` set.
    """
    def on_create(self):
        super().on_create()
        self.style["display"] = "flex"
        self.style["flex-direction"] = "column"
        self.style["border"] = "1px dashed #ccc"
        self.style["gap"] = "10px"
        self.style["flex-direction"] = "column"
        self.klass = 'drag-and-drop'
        
        # Do some magic.
        if "label_text" in self.kwargs:
            label_text = self.kwargs.get('label_text', '')
            self.label = Label(inner_html=label_text)
            self.selected_file_label = Label(
                text="Selected file: No file selected",
                props={"class": 'selected-file-label'},
            )
            self.add_child(self.label)
            self.add_child(self.selected_file_label)
        
        self.inputfield = self.get_kwarg_or_raise('input')
        self.inputfield.style['aria-hidden'] = "true"
        self.inputfield.style["opacity"] = "0"
        self.inputfield.style["width"] = "0"
        self.inputfield.style["height"] = "0"
        self.inputfield.klass = "drag-n-drop-fileinput"
        self.add_child(self.inputfield)
            
        # Now attach script for this drag n drop
        self.script = Script(
            inner_html="""
                function dragAndDropClick(dragAndDrop){
                    const fileInput = $(dragAndDrop).find('input[type="file"]');
                    fileInput.click();
                }
                
                function updateLabelOnFileSelect(fileInput){
                    const dragAndDrop = $(fileInput).closest('.drag-and-drop');
                    const label = dragAndDrop.find('.selected-file-label');
                    const fileName = fileInput.files.length > 0 ? fileInput.files[0].name : 'No file selected';
                    label.text('Selected file: ' + fileName);
                    
                    if (fileName !== 'No file selected'){
                        // change drag and drop color
                        dragAndDrop.css('border-color', 'var(--green)');
                        dragAndDrop.css('border-width', '2px');
                    }
                    else {
                        dragAndDrop.css('border-color', '#ccc');
                        dragAndDrop.css('border-width', '1px');
                    }
                    
                }
                
                // Function to handle the dragover event to allow dropping
                function handleDragOver(event) {
                    event.preventDefault();  // Prevent the default behavior (Prevent file from opening in browser)
                    const dragAndDrop = $(event.target).closest('.drag-and-drop');
                    dragAndDrop.css('border-color', 'var(--green)');  // Highlight border while dragging
                    dragAndDrop.css('border-width', '2px');
                }
                
                // Function to handle the drop event
                function handleDrop(event) {
                    event.preventDefault();  // Prevent the default behavior
                    const dragAndDrop = $(event.target).closest('.drag-and-drop');
                    const fileInput = dragAndDrop.find('input[type="file"]')[0];  // Get the file input element
                    
                    // Get the dropped files
                    const files = event.originalEvent.dataTransfer.files;
                    
                    if (files.length > 0) {
                        // Set the dropped file(s) to the file input field
                        fileInput.files = files;
                
                        // Update the label text
                        updateLabelOnFileSelect(fileInput);
                    }
                    else {
                        dragAndDrop.css('border-width', '1px');
                        dragAndDrop.css('border-color', '#ccc');  // Reset the border color after drop
                    }
                }
                
                $('.drag-and-drop').on('click', function(event){
                    event.stopPropagation();
                    dragAndDropClick(this);
                });
                
                 // Update label text when a file is selected
                $('input[type="file"]').on('change', function(){
                    updateLabelOnFileSelect(this);  // Update the label with the selected file's name
                });

                $('input[type="file"]').on('click', function(event){
                    // Prevent input file click from triggering drag-and-drop click again
                    event.stopPropagation();
                });
                
                // Add event listeners for drag and drop behavior
                $('.drag-and-drop')
                    .on('dragover', handleDragOver)  // Allow dragover event to show the drop area as active
                    .on('drop', handleDrop);  // Handle the drop event when the file is dropped
            """
        )
        
        self.add_child(self.script)
