Web App/CLI → Gateway → Orchestration Service
                                    ↓
Orchestration Service publishes to multiple topics:
├── project.create → Project Service (create the project on the database and the directory)
├── infrastructure.provision → Infrastructure Service (create the infrastructure neeeded such as the virtual machines or docker containers depending on what the user prefers, using libvirt)
├── environment.development.create → Environment Service (This will use devbox by jetify to create the dvelopment environment locally on the user's machine at on the directory created, with the technologies the user specifies)
├── environment.production.create → Environment Service (This will use libvirt to ssh on the virtual machines for production and install the tools needed to build the project for production or testing environment, based on the tools the user specifies)
├── components.deploy → Component Service (with jinja2 this will generate the actual project files like django urls, angular services and the likes)

