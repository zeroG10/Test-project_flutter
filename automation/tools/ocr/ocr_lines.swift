// Text lines on screenshots, with their boxes in image pixels (origin top-left), as JSON lines on stdout:
//   {"file": "...", "width": 1080, "height": 2400, "lines": [{"text": "...", "box": [x0, y0, x1, y1]}]}
// macOS Vision, on the machine: nothing leaves it. Used by redact_screens.py to find personal data to pixelate.
import Foundation
import Vision
import AppKit

func lines(of path: String) -> [String: Any]? {
    guard let image = NSImage(contentsOfFile: path),
          let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return nil }
    let w = CGFloat(cg.width), h = CGFloat(cg.height)
    var out: [[String: Any]] = []
    let request = VNRecognizeTextRequest { req, _ in
        for case let obs as VNRecognizedTextObservation in req.results ?? [] {
            guard let top = obs.topCandidates(1).first else { continue }
            let b = obs.boundingBox
            out.append(["text": top.string,
                        "box": [Int(b.minX * w), Int((1 - b.maxY) * h), Int(ceil(b.maxX * w)), Int(ceil((1 - b.minY) * h))]])
        }
    }
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([request])
    return ["file": path, "width": cg.width, "height": cg.height, "lines": out]
}

for path in CommandLine.arguments.dropFirst() {
    if let result = lines(of: path),
       let data = try? JSONSerialization.data(withJSONObject: result),
       let text = String(data: data, encoding: .utf8) {
        print(text)
    }
}
