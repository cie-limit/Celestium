class Vehicle:
    def __init__(self, name, dry_mass, isp, fuel_capacity, img_url, description):
        self.name = name
        self.mass = dry_mass
        self.isp = isp
        self.fuel_capacity = fuel_capacity
        self.img_url = img_url
        self.description = description

    def get_description(self):
        return f"""
        <div style="color: #aaddff;">
        <b>Dry Mass:</b> {self.mass:,} kg<br>
        <b>ISP:</b> {self.isp} s<br>
        <b>Fuel Cap:</b> {self.fuel_capacity:,} kg
        <br><br>{self.description}
        </div>
        """

VEHICLES = {
    "SpaceX Starship": Vehicle(
        "SpaceX Starship",
        dry_mass=120000, 
        isp=380,         
        fuel_capacity=1200000,
        # 사용자 제공 URL
        img_url="https://images-assets.nasa.gov/image/KSC-71PC-0571/KSC-71PC-0571~large.jpg?w=1920&h=1536&fit=crop&crop=faces%2Cfocalpoint", 
        description="Fully reusable. Optimization assumes orbital refueling is complete."
    ),
    "Apollo Saturn V": Vehicle(
        "Apollo Saturn V",
        dry_mass=130000,
        isp=421,          
        fuel_capacity=110000,
        # 사용자 제공 URL
        img_url="https://images-assets.nasa.gov/image/KSC-71PC-0571/KSC-71PC-0571~large.jpg?w=1920&h=1536&fit=crop&crop=faces%2Cfocalpoint",
        description="Expendable 3-stage rocket. S-IVB stage used for TLI."
    ),
    "SLS Block 1B": Vehicle(
        "SLS Block 1B",
        dry_mass=125000, 
        isp=460,          
        fuel_capacity=130000,
        # 사용자 제공 URL
        img_url="https://cdn.jetphotos.com/full/5/1491940_1712030325.jpg",
        description="NASA's Super Heavy-Lift Launch Vehicle (Artemis)."
    )
}
