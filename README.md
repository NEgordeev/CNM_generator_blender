Carbon nanomaterials generator v0.2

<img width="1561" height="861" alt="image" src="https://github.com/user-attachments/assets/e1d65c34-825f-4f06-815a-795ccbc560c9" />

For the CNTs you may want to adjust an agle a little bit in simple deform modifier, since now it is a simple linear approximation

For the CNT films for now you may want to use a boolean cube (or any other shape) to adjust the edges.

For the CNT films you also need to install Blender add-on called "Extra Curve Objects", since it uses bounce spline from it. I am not an author of this add-on and you may want to check the website: https://extensions.blender.org/add-ons/extra-curve-objectes/?utm_source=blender-4.5.3-lts

If you want to deform your tube, place any deform modifiers before the geometry node

For graphene - you can adjust the flake shape through the edit mode. There is a floating carbon atom - hard to change via code, but easy to fix: Make in this face an triangle from the 
  
1) <img width="337" height="247" alt="image" src="https://github.com/user-attachments/assets/fbd3a4ac-af86-47e0-8403-530a79fdf385" />

2) <img width="327" height="269" alt="image" src="https://github.com/user-attachments/assets/156b9bf9-711a-4801-95c6-417f6332bf75" />

3) <img width="556" height="385" alt="image" src="https://github.com/user-attachments/assets/13913e3b-38f1-45d3-a2eb-9d36cffe0372" />

4) <img width="329" height="255" alt="image" src="https://github.com/user-attachments/assets/a05b9864-8406-4de8-8b78-7cc100ae4c9e" />
