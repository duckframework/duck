"""
File Input components module (including FileDragAndDrop component).
"""
from duck.html.components.theme import Theme
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
        self.props.update({"type": "file"})


class FileDragAndDrop(Card):
    """
    File Drag N Drop component with capabilities of dropping files rather than selecting only.

    Args:
        label_text (str): Text for the file drag n drop component
        input (FileInput): FileInput component with properties like `name` set.
    """

    # Drag and drop behavior for the component, kept as a class constant
    # since it is static markup shared by every instance.
    DRAG_AND_DROP_SCRIPT = """
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

    def on_create(self):
        super().on_create()

        # Container setup
        self.klass = "drag-and-drop"
        self.style.update({
            "display": "flex",
            "flex-direction": "column",
            "border": f"1px dashed {Theme.current.border_color}",
            "gap": Theme.current.spacing,
        })

        # Label and selected-file indicator
        if "label_text" in self.kwargs:
            label_text = self.kwargs.get("label_text", "")
            
            # Initialize labels
            self.label = Label(text=label_text)
            self.selected_file_label = Label(
                text="Selected file: No file selected",
                klass="selected-file-label",
            )
            
            # Add labels
            self.add_children([self.label, self.selected_file_label])

        # File input field
        self.input = self.get_kwarg_or_raise("input")
        self.input.klass = "drag-n-drop-fileinput"
        
        # Update input field style
        self.inputfield.style.update({
            "aria-hidden": "true",
            "opacity": "0",
            "width": "0",
            "height": "0",
        })
        
        # Drag and drop script
        self.script = Script(inner_html=self.DRAG_AND_DROP_SCRIPT)
        
        # Add children
        self.add_child([self.input, self.script])
