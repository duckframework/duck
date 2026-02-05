document.addEventListener("DOMContentLoaded", function () {
  // Verify if the Sphinx-provided `version-list` element exists
  const versionList = document.getElementById("version-list");
  if (!versionList) {
    console.error("Version data not found.");
    return;
  }

  // Parse versions data from the script tag
  const versions = JSON.parse(versionList.textContent);

  // Create a floating version picker container
  const versionPicker = document.createElement("div");
  versionPicker.id = "version-picker";
  versionPicker.style.position = "fixed";
  versionPicker.style.bottom = "80px";
  versionPicker.style.right = "20px";
  versionPicker.style.backgroundColor = "black";
  versionPicker.style.color = "#ffffff";
  versionPicker.style.border = "1px solid #ddd";
  versionPicker.style.padding = "4.5px";
  versionPicker.style.borderRadius = "5px";
  versionPicker.style.boxShadow = "0px 2px 5px rgba(0, 0, 0, 0.2)";
  versionPicker.style.zIndex = "1000";

  // Create label element for the dropdown
  const label = document.createElement("label");
  label.innerText = "Version ";
  label.style.marginRight = "5px";

  // Create the dropdown
  const dropdown = document.createElement("select");
  dropdown.style.padding = "5px";
  dropdown.style.background = "transparent";
  dropdown.style.borderLeft = "1px solid #ddd";
  dropdown.style.color = "#ddd";
  
  // Populate the dropdown with versions from Sphinx's context
  versions.forEach(version => {
    const option = document.createElement("option");
    option.value = version.url;
    option.textContent = version.name;

    // Mark the current version as selected
    if (window.location.pathname.endsWith(version.url)) {
      option.selected = true;
    }
    dropdown.appendChild(option);
  });

  // Navigate to the selected version on change
  dropdown.addEventListener("change", function () {
    window.location.href = this.value;
  });

  // Add elements to the version picker
  versionPicker.appendChild(label);
  versionPicker.appendChild(dropdown);

  // Append the version picker to the body
  document.body.appendChild(versionPicker);
});
