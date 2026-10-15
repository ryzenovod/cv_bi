// macOS native QR verification. No network requests.
import Foundation
import CoreImage
let detector = CIDetector(ofType: CIDetectorTypeQRCode, context: nil,
                         options: [CIDetectorAccuracy: CIDetectorAccuracyHigh])!
let expected = "https://ryzenovod.github.io/cv_bi/"
for path in CommandLine.arguments.dropFirst() {
    guard let image = CIImage(contentsOf: URL(fileURLWithPath:path)) else {
        fatalError("Could not read image: \(path)")
    }
    let values = detector.features(in:image).compactMap { ($0 as? CIQRCodeFeature)?.messageString }
    guard values.contains(expected) else { fatalError("QR mismatch at \(path): \(values)") }
    print("PASS \(URL(fileURLWithPath:path).lastPathComponent): \(expected)")
}
