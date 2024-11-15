def init_bundle(self):
    bundle = {}
    bundle["name"] = "bundle1"
    bundle["data"] = [
      ["case1",    self.case1]
    ]
    self.bundle_map[bundle["name"]]=bundle
    
    bundle = {}
    bundle["name"] = "bundle2"
    bundle["data"] = [
     ["case1",    self.case2]
    ]
    self.bundle_map[bundle["name"]]=bundle
    